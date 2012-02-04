#!/usr/bin/env python

import sys
sys.path.append('../nxtemu/')
sys.path.append('../nxted/')
import yaml, re
from string import Template

LATEX_DOC_TEMPLATE = """
\\documentclass[10pt,a4paper]{article}
\\usepackage[utf8]{inputenc}
\\usepackage[Bjarne]{fncychap}                                                 
\\usepackage[parfill]{parskip}

\\title{$title}
\\author{$author}
\\date{}

\\begin{document}
\\maketitle
$text

\\end{document}
"""

LATEX_FUNCTION_TEMPLATE = """
{\\bf $func}({\it $args}) 
$desc
$items
"""

LATEX_ARGS_ITEMS_TEMPLATE = """
\\begin{quote}
    \\begin{itemize}
        $items
    \\end{itemize}
\\end{quote}

"""

LATEX_ARG_ITEMS_TEMPLATE = """
\\item \\textbf{$name} ({\emph{$type}}) $desc
"""


def getAPI():
    """Returns a list of available functions for NXT brick. """
    
    out = {}
    
    api = __import__('api')

    for func in dir(api):
        if func[0].isupper():
            id = getattr(api, func)
            if type(id).__name__ == "function":
                out[func] = id.__doc__

    
    return out


def exportYaml(fname = '../nxtemu/help.yml'):
    api = getAPI()

    for func,desc in api.iteritems():
        api[func] = desc.replace(':param ', '')
        
    f = open(fname, 'w')
    f.write(yaml.dump(api, default_flow_style=False))
    f.close() 

    return fname

def exportLatex(fname = 'reference.tex'):
    api = getAPI()
    
    document_template = Template(LATEX_DOC_TEMPLATE)
    function_template = Template(LATEX_FUNCTION_TEMPLATE)
    args_template = Template(LATEX_ARG_ITEMS_TEMPLATE)
    arg_items_template = Template(LATEX_ARGS_ITEMS_TEMPLATE)
    
    funcs = ''

    for func,desc in api.iteritems():
        args = desc.split('\n')[0].split('(')[1][:-1]

        desc = desc.split('\n')[1:]
        desc = '\n'.join(desc)

        matches = re.findall(":param (.*?) (.*?): (.*)", desc)
        items = ''
        if matches != []:
            for match in matches:
                items += args_template.safe_substitute(name=match[1],
                                                       type=match[0],
                                                       desc=match[2])

        desc = re.sub(".*:param .*", '', desc)

        if items != '':
            generated_items  = arg_items_template.safe_substitute(items=items)
        else:
            generated_items = ''

        funcs += function_template.safe_substitute(func=func, 
                                                   args=args, 
                                                   desc=desc,
                                                   items=generated_items)


    
    
    document = document_template.safe_substitute(text=funcs, 
                                                title="nxtIDE reference manual",
                                                author="XLC Team")

    f = open(fname, 'w')
    f.write(document)
    f.close() 

    return fname




if __name__ == "__main__":
    if len(sys.argv) == 1:
        print "Please specify target:"
        print "\tlatex"
        print "\tyaml"
        sys.exit()

    if sys.argv[1] == 'yaml':
        if len(sys.argv) > 2:
            file = exportYaml(sys.argv[2])
        else:
            file = exportYaml()

    elif sys.argv[1] == 'latex':
        if len(sys.argv) > 2:
            file = exportLatex(sys.argv[2])
        else:
            file = exportLatex()

    else:
        print "Unknown format"
        sys.exit()

    print "Output written to ", file

   