import gensim
import logging
import helper
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import numpy as np
import codecs

import matplotlib
zhfont1 = matplotlib.font_manager.FontProperties(fname='/System/Library/Fonts/STHeiti Light.ttc')

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def build_phrases():
    data = list(helper.load_data_from_file().values())

    sentence_stream = helper.create_sent_stream(data, False)

    phrases = gensim.models.Phrases(sentence_stream, min_count=10, threshold=100)
    bigram = gensim.models.phrases.Phraser(phrases)

    # vocab = dict()
    # ssss = 0
    # for phrase, score in phrases.export_phrases(sentence_stream):
    #     vocab[phrase.decode('utf-8')] = score
    #     ssss += score
    #
    # sorted_dic = [(k, vocab[k]) for k in sorted(vocab, key=vocab.get, reverse=True)]
    #
    # print(sorted_dic)
    # print(len(sorted_dic))
    # print('sum:' + str(ssss))
    # return
    #
    # with open('phrase.txt', 'w') as f:
    #     f.write(s)
    #     f.close()

    return bigram, sentence_stream


def load_model():
    try:
        model = gensim.models.Word2Vec.load('vec.mdl')
        return model

    except FileNotFoundError:
        print('Building new model...\n')
        bigram, sentence_stream = build_phrases()
        corpus = list(bigram[sentence_stream])

        model = gensim.models.Word2Vec(corpus, min_count=5, size=100, workers=4)
        model.save('vec.mdl')

    return model


def plot_vocab_with_tsne(model):

    wv = model.wv
    random_vocab = (model.wv.vocab.keys())

    X = None
    vocabulary = None
    try:
        vocabulary, X = zip(*[(it, wv[it]) for it in random_vocab if wv.__contains__(it)])
    except KeyError:
        pass

    tsne = TSNE(n_components=2, random_state=0)
    np.set_printoptions(suppress=True)
    Y = tsne.fit_transform(X)

    plt.scatter(Y[:, 0], Y[:, 1])
    for label, x, y in zip(vocabulary, Y[:, 0], Y[:, 1]):
        plt.annotate(label, xy=(x, y), xytext=(0, 0), textcoords='offset points', fontproperties=zhfont1)

    plt.show()

    return


def test_model(model, arg_name, arg_value, words=('玉','云','马','凤_凰')):
    s = '\n\nTesting: ' + str(arg_name) + '=' + str(arg_value) + '.............\n'

    for w in words:
        s += '和（' + w + '）最接近的10个词为： ' + str(model.wv.most_similar(w, topn=10)) + '\n'

    try:
        f = codecs.open('test.txt', 'a', encoding='utf-8')
        f.write(s)
        f.close()
    except IOError as e:
        f.close()
        print(e)

    print(s)

    return

#model = load_model()

def optimaze_model():

    bigram, sentence_stream = build_phrases()
    corpus = list(bigram[sentence_stream])

    p = dict()
    p['min_count'] = (2, 5, 10)
    p['size'] = (80, 100, 200)

    # learning rate by default = 0.025
    p['alpha'] = (0.01, 0.025, 0.05)

    p['window'] = (5, 7, 9)
    p['iter'] = (5, 10)

    # sg = 1 for skip_gram
    p['sg'] = (0, 1)

    # number of nagtive words
    p['negative'] = (5, 10)

    # threshold for configuring which higher-frequency words are randomly downsampled;
    p['sample'] = (1e-4, 1e-3, 1e-2)

    for para_name in p.keys():
        for para_value in p[para_name]:
            args = {'sentences': corpus, para_name: para_value}

            print('Building Model: ' + str(para_name) + '=' + str(para_value) + '.............')

            try:
                model = gensim.models.Word2Vec(**args)
                test_model(model, para_name, para_value)
                del model
            except Exception as e:
                print(e)


    return

#print(model.wv.vocab.keys())


#plot_vocab_with_tsne(model)

model = load_model()
print(model.wv.most_similar(positive=['日', '天'], negative=['月']))
print(model.wv.most_similar(positive=['东', '日'], negative=['西']))
print(model.wv.most_similar(positive=['绿', '竹'], negative=['杨']))

#optimaze_model()