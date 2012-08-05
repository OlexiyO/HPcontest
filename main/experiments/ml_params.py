import os
import time
import numpy
from main.base import util
from main.io import signal
from main.io.signal import G
from main.metrics import kappa

__author__ = 'Olexiy Oryeshko (olexiyo@gmail.com)'


from main.algo import grad_boost
import gflags
FLAGS = gflags.FLAGS
gflags.DEFINE_string('graph_dir', 'C:\\Dev\\Kaggle\\asap-sas\\graphs', '')

def Render(to_render, title=''):
  # args: list of (data, color) pairs.
  import pylab as pl
  pl.figure()
  for data, color, label in to_render:
    pl.plot(range(len(data)), data, '-', color=color, label=label)
  pl.legend(loc='center')
  pl.xlabel(title)
  fpath = os.path.join(FLAGS.graph_dir, '%s.png' % time.time())
  pl.ylabel('Cost')
  pl.savefig(fpath)
  pl.show()


def RenderPredictorProgress(av_p, boost_params, filter_train, list_of_signals, q, steps):
  filter_test = lambda id: not filter_train(id)

  signals_train = signal.ListOfSignals(list_of_signals, q, extra_filter=filter_train)
  signals_test = signal.ListOfSignals(list_of_signals, q, extra_filter=filter_test)
  scores_train = G.score.ValuesForQuestion(q, extra_filter=filter_train)
  scores_test = G.score.ValuesForQuestion(q, extra_filter=filter_test)
  kappa_train, kappa_test, loss_train, loss_test = [], [], [], []
  predictions_train = av_p.PredictionAtSteps(signals_train)
  predictions_test = av_p.PredictionAtSteps(signals_test)
  for step in range(steps):
    pred_train = predictions_train[step]
    pred_test = predictions_test[step]
    kappa_train.append(kappa.quadratic_weighted_kappa(util.IntRound(pred_train), scores_train))
    kappa_test.append(kappa.quadratic_weighted_kappa(util.IntRound(pred_test), scores_test))
    loss_train.append(av_p.Loss(numpy.array(pred_train), numpy.array(scores_train)))
    loss_test.append(av_p.Loss(numpy.array(pred_test), numpy.array(scores_test)))
  Render([(kappa_train, 'blue', 'kappa_train'), (kappa_test, 'purple', 'kappa_test: %.2f' % max(kappa_test)),
    (loss_train, 'red', 'loss_train'), (loss_test, 'orange', 'loss_test')],
    title='%s' % boost_params)


def PlotNumberOfEstimators(q, list_of_signals, mods_for_training=None, boost_params=None, steps=100):
  # Trains model with params and with big numbers of steps. Then renders kappa + model loss after each step.
  if boost_params is None:
    boost_params = {}
  if mods_for_training is None:
    mods_for_training = range(4)
  preds = [grad_boost.Approximate(list_of_signals, q, extra_filter=util.FMod(k), boost_params=boost_params)
           for k in mods_for_training]
  filter_for_training = util.FMods(mods_for_training)
  av_p = grad_boost.AveragePredictor(preds, [util.FMod(k) for k in mods_for_training])
  RenderPredictorProgress(av_p, boost_params, filter_for_training, list_of_signals, q, steps=steps)
