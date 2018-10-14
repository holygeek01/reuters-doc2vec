'''
this script use the trained model to predict the category of the news
'''
import nltk
import numpy
from gensim.models import Doc2Vec
from keras.models import load_model
from nltk.corpus import reuters
from nltk.tokenize import word_tokenize
from sklearn.preprocessing.label import MultiLabelBinarizer
import logging 
logging.basicConfig(level='INFO')
logger=logging.getLogger(__name__)

doc2vec_model_location = 'vectors/doc2vec-vectors.bin'
classifier_model_location = 'models/classifier-model.bin'

# Use the doc2vec model created in reuters-classifier-train.py
doc2vec = Doc2Vec.load(doc2vec_model_location)
logger.info('doc2vec model loaded')
# Load the test articles and convert it to doc vectors
test_articles = [{'raw': reuters.raw(fileId), 'categories': reuters.categories(fileId)} for fileId in reuters.fileids() if fileId.startswith('test/')]
test_data = [doc2vec.infer_vector(word_tokenize(article['raw'])) for article in test_articles]
logger.info('test data loaded')
# Initialize the neural network
model=load_model(classifier_model_location)
logger.info('classifier loaded')

# Make predictions
predictions = model.predict(numpy.asarray(test_data))

# Convert the prediction with gives a value between 0 and 1 to exactly 0 or 1 with a threshold
predictions[predictions<0.5] = 0
predictions[predictions>=0.5] = 1

# Convert predicted classes back to category names
labelBinarizer = MultiLabelBinarizer()
labelBinarizer.fit([reuters.categories(fileId) for fileId in reuters.fileids()])
predicted_labels = labelBinarizer.inverse_transform(predictions)

for predicted_label, test_article in zip(predicted_labels, test_articles):
    print('title: {}'.format(test_article['raw'].splitlines()[0]))
    print('predicted: {} - actual: {}'.format(list(predicted_label), test_article['categories']))
    print('')