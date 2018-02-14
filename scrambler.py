import os, sys, random, yaml
import numpy as np

""" 
  Load data/parameters
"""
config = yaml.load(open("config.yml"))
if len(sys.argv) == 2:
    config["file"] = sys.argv[1]
F = [line.strip() for line in open(config["file"],'r')]

"""
  Scrambling functions
"""
def swap(w, probability=1.0):
  """
    Random swap two letters in the middle of a word
  """
  if random.random() > probability:
    return w
  if len(w) > 3:
    w = list(w)
    i = random.randint(1, len(w) - 3)
    w[i], w[i+1] = w[i+1], w[i]
    return ''.join(w)
  else:
    return w

def random_middle(w):
  """
    Randomly permute the middle of a word (all but first and last char)
  """
  if len(w) > 3:
    middle = list(w[1:len(w)-1])
    random.shuffle(middle)
    middle = ''.join(middle)
    return w[0] + middle + w[len(w) - 1]
  else:
    return w

def fully_random(w, percentage=1.0):
  if random.random() > percentage:
    return w
  """
    Completely random permutation
  """
  w = list(w)
  random.shuffle(w)
  return ''.join(w)

NN = {}
for line in open("noise/" + config["lang"] + ".key"):
  line = line.split()
  NN[line[0]] = line[1:]
def key(w, probability=1.0):
  if random.random() > probability:
    return w
  """
    Swaps $n$ letters with their nearest keys
  """
  w = list(w)
  i = random.randint(0, len(w) - 1)
  char = w[i]
  caps = char.isupper()
  if char in NN:
    w[i] = NN[char.lower()][random.randint(0, len(NN[char.lower()]) - 1)]
    if caps:
      w[i].upper()
  return ''.join(w)

typos = {}
for line in open("noise/" + config["lang"] + ".natural"):
  line = line.strip().split()
  typos[line[0]] = line[1:]
def natural(w, precentage=1.0):
  if random.random() > precentage:
    return w
  if w in typos:
    return typos[w][random.randint(0, len(typos[w]) - 1)]
  return w

def scrambling(choice):
  """
    Lookup scrambling function
  """
  if choice == "swap":
    return swap
  elif choice == "key":
    return key
  elif choice == "middle":
    return random_middle
  elif choice == "random":
    return fully_random
  elif choice == "real":
    return natural
  elif choice == "vanilla":
    return lambda y: y
  else:
    print("Invalid scrambling ", choice)
    sys.exit()

"""
  Process Data
"""
def iterate_through(text):
  text = text.strip().split()
  processed = []

  if sum(config["distribution"]) > 1:
    for op, percent in zip(config["scrambling"], config["distribution"]):
      if random.random() < percent:
          foo = scrambling(op)
          processed.append(" ".join([foo(w) for w in text]))
  elif sum(config["distribution"]) == 1:
    op = np.random.choice(config["scrambling"], p=config["distribution"])
    foo = scrambling(op)
    processed.append(" ".join([foo(w) for w in text]))
  else:
    r = random.random()
    for op, percent in zip(config["scrambling"], config["distribution"]):
      if r < percent:
          foo = scrambling(op)
          processed.append(" ".join([foo(w) for w in text]))
      else:
        r -= percent
  return processed

out = open("%s.%s.%s" % (config["file"].split("." + config["ftype"])[0], 
                                "_".join(config["scrambling"]), 
                                config["ftype"]), 'w')
if config["ftype"] == "sgm":
  for line in F:
    spl = line.split()
    if spl[0] != "<seg":
      out.write(line + "\n")
    else:
      start = line.find(">")
      end = line.rfind("<")

      seg_id = line[:start+1]
      text = line[start + 1:end]
      close = line[end:]

      for sentence in iterate_through(text):
          out.write("%s%s%s\n" % (seg_id, sentence, close))
  out.close()
elif config["ftype"] == "txt":
  for line in F:
    for sentence in iterate_through(line):
      out.write("%s\n" % (sentence))
  out.close()
else:
  print("Unknown file type", ftype)
  sys.exit()
