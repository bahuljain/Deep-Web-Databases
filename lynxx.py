from subprocess import Popen, PIPE
import re

def getPageContent(url):
    p = Popen(["lynx", "--dump", url], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate()
    return output if not err else None

def cleanContent(url):
    content = getPageContent(url)
    end = content.index("\nReferences\n")
    content = content[:end]
    content = re.sub(r'\[(.*?)\]', '', re.sub(r'\n', "", content))
    vocab = set([w.lower() for w in re.split(r'\W+', content) if str.isalpha(w)])
    return vocab


if __name__ == '__main__':
    url = "http://www.cs.columbia.edu/~gravano/cs6111/proj2.html"
    print cleanContent(url)
