import torch
from torchtext import data, datasets
import torchtext
from collections import Counter, defaultdict
PAD_WORD = '<blank>'
UNK = 0
BOS_WORD = '<s>'
EOS_WORD = '</s>'

def __getstate__(self):
    return dict(self.__dict__, stoi=dict(self.stoi))


def __setstate__(self, state):
    self.__dict__.update(state)
    self.stoi = defaultdict(lambda: 0, self.stoi)


torchtext.vocab.Vocab.__getstate__ = __getstate__
torchtext.vocab.Vocab.__setstate__ = __setstate__

def load_fields(vocab):
    vocab = dict(vocab)
    fields = get_fields()
    for k, v in vocab.items():
        # Hack. Can't pickle defaultdict :(
        v.stoi = defaultdict(lambda: 0, v.stoi)
        fields[k].vocab = v
    return fields

def save_vocab(fields):
    vocab = []
    for k, f in fields.items():
        if 'vocab' in f.__dict__:
            f.vocab.stoi = dict(f.vocab.stoi)
            vocab.append((k, f.vocab))
    return vocab


def get_fields():

    fields = {}
    fields["src"] = torchtext.data.Field(pad_token=PAD_WORD,include_lengths=True)
    fields["tgt"] = torchtext.data.Field(init_token=BOS_WORD, eos_token=EOS_WORD,pad_token=PAD_WORD)
    return fields

class OrderedIterator(torchtext.data.Iterator):
    def create_batches(self):
        if self.train:
            self.batches = torchtext.data.pool(
                self.data(), self.batch_size,
                self.sort_key, self.batch_size_fn,
                random_shuffler=self.random_shuffler)
        else:
            self.batches = []
            for b in torchtext.data.batch(self.data(), self.batch_size,
                                          self.batch_size_fn):
                self.batches.append(sorted(b, key=self.sort_key))


class NMTDataset(data.TabularDataset):
    @staticmethod
    def sort_key(ex):
        "Sort in reverse size order"
        return -len(ex.src)


    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__.update(d)

    def __reduce_ex__(self, proto):
        "This is a hack. Something is broken with torch pickle."
        return super(NMTDataset, self).__reduce_ex__()
    

