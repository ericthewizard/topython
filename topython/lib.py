import logging
from time import sleep
import os
import openai
from .prompts import PROMPT_START, PROMPT_HEADER, prompts

openai.api_key = os.getenv("OPENAI_API_KEY")
logging.basicConfig(format='%(asctime)s: %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)


def split_line_tokens(line):
    return [item.strip().lower() for item in line.split(' ')]


def split_file(filetxt):
    """
    splits text with multiple IDL procedures/functions
    into a list of individual procedures/functions

    kludgy, but works most of the time
    """
    if 'end\n' not in filetxt.lower():
        return [filetxt]
    out = []
    filelines = filetxt.split('\n')
    for line in filelines:
        if line.lower().strip() == 'end':
            out.append('end')
        else:
            out.append(line)

    items = []
    current = []
    # keep track of case statements, since those can have end's in them
    case = False

    for line in out:
        current.append(line)
        tokens = split_line_tokens(line)
        if 'case' in tokens:
            case = True
        if 'endcase' in tokens:
            case = False
        if 'end' in tokens:
            if not case:
                # should be the end of the function
                items.append('\n'.join(current))
                current = []
    return items


def estimate_tokens(text):
    """
    estimates the number of tokens in some text

    this estimate is from:
        https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them
    """
    return len(text) / 4.0


def get_prompt(text, header=False):
    """
    generates the input to send to the model
    """
    if header:
        out = PROMPT_START + PROMPT_HEADER
    else:
        out = PROMPT_START
    for prompt in prompts.keys():
        if prompt in text.lower():
            out = out + prompts[prompt]
    out = out + '\nIDL:\n' + text + '\n' + """\nPython:\n"""
    return out


def convert(file,
            raw=False,
            max_tokens=4096,
            best_of=5,
            header=True,
            dynamic_tokens=True,
            token_padding=0.61,
            tmp_output=False):
    """

    """
    if not raw:
        directory, filename = os.path.split(file)
        out_file = filename[:-4] + '.py'
        filetxt = open(file, 'r').read()
    else:
        filetxt = file

    if header:
        logging.info('including header example...')

    items = split_file(filetxt)

    logging.info('number of functions/procedures: ' + str(len(items)))
    out = ''

    for index, item in enumerate(items):
        logging.info('item #' + str(index + 1))
        prompt = get_prompt(item, header=header)

        initial_estimate = max_tokens

        if dynamic_tokens:
            initial_estimate = estimate_tokens(prompt)
            logging.info('initial estimate of number of tokens: ' + str(int(initial_estimate)))
            num_tokens = initial_estimate
            num_tokens += token_padding * num_tokens
            logging.info('approximate number of output tokens: ' + str(int(num_tokens)))
        else:
            num_tokens = max_tokens

        if num_tokens * 2 > 8001 and dynamic_tokens:
            num_tokens = 8001 - (initial_estimate + initial_estimate * token_padding)
            logging.info('limiting the number of output tokens: ' + str(int(num_tokens)))

        logging.info('estimate of the total number of tokens (input + output): ' + str(
            int(num_tokens + initial_estimate + initial_estimate * token_padding)))

        response = openai.Completion.create(
            model="code-davinci-002",
            prompt=prompt,
            temperature=0,
            max_tokens=int(num_tokens),
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            best_of=best_of
        )

        output = response['choices'][0]['text']
        full_output = output

        # search for excess code at the end
        if 'IDL:\n' in output:
            logging.info('removing excess at the end of the output...')
            output = output[:output.find('IDL:\n')]

        if tmp_output and not raw:
            # useful for debugging strange output
            with open(os.path.join(directory, filename[:-4] + '_tmp_full_' + str(index) + '.py'), 'w') as f:
                f.write(full_output)
            with open(os.path.join(directory, filename[:-4] + '_tmp_' + str(index) + '.py'), 'w') as f:
                f.write(output)
            with open(os.path.join(directory, filename[:-4] + '_prompt_' + str(index) + '.pro'), 'w') as f:
                f.write(prompt)

        out = out + '\n\n' + output

    if raw:
        return out

    with open(os.path.join(directory, out_file), 'w') as f:
        f.write(out)

    logging.info('done!')
    logging.info('output: ' + os.path.join(directory, out_file))


def convert_folders(folder=None, max_tokens=4096, skip_existing=True, header=True):
    """
    convert all folders and subfolders
    """
    if folder is None:
        logging.error('No folder specified.')
        return

    for dirpath, dirnames, filenames in os.walk(folder):
        for filename in [f for f in filenames if f.endswith(".pro")]:
            if skip_existing:
                if os.path.isfile(os.path.join(dirpath, filename[:-4] + '.py')):
                    continue
            logging.info('processing: ' + filename)
            try:
                convert(os.path.join(dirpath, filename), max_tokens=max_tokens, header=header)
            except:
                logging.error('problem with: ' + os.path.join(dirpath, filename))
                continue
            # sleep for 30 seconds to avoid hitting the API's rate limits
            sleep(30)


