import math
from main.io.olefeature import G
from main.metrics.metrics import Eval

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'


def Func(id, vars):
  return vars['a'] * G.num_words[id] + vars['b'] * G.word_length[id]


def DoMe(Func, vars, questions, filter, step):
  def RealF(v):
    return Cost(Func, v, questions, filter)
  return GradientDescent(RealF, vars, num_steps=10, step=1e-7)


def Gradient(target, vars, step=1e-8):
  value = target(vars)
  grad = {}
  for k in vars:
    vars[k] += step
    dk = (target(vars) - value) / step
    if abs(dk) > 1e-5:
      grad[k] = dk
    vars[k] -= step
  norm = math.sqrt(sum(v*v for v in grad.itervalues()))
  for k in grad:
    grad[k] /= norm
  return grad   


def GradientDescent(target, ivars, num_steps=10, step=1e-6):
  # TODO: compare with validation set.
  M = num_steps / 10
  vars = ivars.copy()
  for n in xrange(num_steps):
    if n % M == 0:
      print 'Step %d. Value: %d. Vars: %s' % (n, target(vars), vars)

    grad = Gradient(target, vars)
    if not grad:
      return vars
    vars = MoveInDirection(target, grad, vars, step)
  return vars


def MoveInDirection(target, grad, ivars, istep):
  value = target(ivars)
  vars = ivars.copy()
  M = 1.
  while M >= 1:
    for k, v in grad.iteritems():
      vars[k] -= v * istep * M
    new_value = target(vars)
    if new_value < value:
      value = new_value
      M *= 2
    else:
      for k, v in grad.iteritems():
        vars[k] += v * istep * M
      M /= 2

  return vars


def Cost(Func, vars, questions, filter):
  assert questions
  assert vars
  results = [Func(ind, vars) for ind, q in enumerate(G.question) if q in questions and filter(ind)]
  return Eval(results, filter, questions)
