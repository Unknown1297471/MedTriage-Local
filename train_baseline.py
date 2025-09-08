# train_baseline.py: retrain the baseline model from CSV
import json, argparse, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import f1_score
from joblib import dump

def main(args):
    df = pd.read_csv(args.data)
    train = df[df.split == 'train'].copy()
    val = df[df.split == 'val'].copy()
    X_train_text = train['symptoms_text'].values
    X_val_text = val['symptoms_text'].values
    mlb = MultiLabelBinarizer()
    Y_train = mlb.fit_transform(train['top_conditions'].apply(lambda s: [x.strip() for x in str(s).split(',') if x.strip()]).values)
    Y_val = mlb.transform(val['top_conditions'].apply(lambda s: [x.strip() for x in str(s).split(',') if x.strip()]).values)
    vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1,2), max_features=20000, strip_accents='unicode', min_df=2, sublinear_tf=True)
    X_train = vectorizer.fit_transform(X_train_text)
    X_val = vectorizer.transform(X_val_text)
    clf = OneVsRestClassifier(LogisticRegression(max_iter=2000, C=2.0, class_weight='balanced', solver='liblinear'))
    clf.fit(X_train, Y_train)
    Y_val_pred = clf.predict(X_val)
    macro_f1 = f1_score(Y_val, Y_val_pred, average='macro', zero_division=0)
    micro_f1 = f1_score(Y_val, Y_val_pred, average='micro', zero_division=0)
    print({'macro_f1_val': round(float(macro_f1),4), 'micro_f1_val': round(float(micro_f1),4)})
    dump(vectorizer, 'vectorizer.joblib'); dump(clf, 'classifier.joblib'); dump(mlb, 'mlb.joblib')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='medtriage_dataset.csv')
    args = parser.parse_args()
    main(args)
