"""Reproducible Salifort Motors employee attrition analysis."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix, ConfusionMatrixDisplay,
    PrecisionRecallDisplay)
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports'
FIG = OUT / 'figures'
SEED = 42

def load_data():
    OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
    raw = pd.read_csv(ROOT / 'data/HR_comma_sep.csv')
    df = raw.rename(columns={'Work_accident':'work_accident', 'average_montly_hours':'average_monthly_hours',
        'time_spend_company':'tenure', 'Department':'department'})
    assert set(df.left.unique()) == {0,1}, 'Target must be binary'
    audit = {'raw_rows':len(df), 'columns':len(df.columns), 'duplicate_rows':int(df.duplicated().sum()),
        'missing_cells':int(df.isna().sum().sum()), 'raw_attrition_rate':float(df.left.mean())}
    # No employee identifier exists: deduplicate exact records as an explicit analysis assumption.
    df = df.drop_duplicates().reset_index(drop=True)
    audit.update(clean_rows=len(df), attrition_rate=float(df.left.mean()))
    (OUT/'data_audit.json').write_text(json.dumps(audit,indent=2))
    print(json.dumps(audit,indent=2))
    return df, audit

def explore(df):
    tables = {}
    for col in ['department','salary','number_project','tenure']:
        table = df.groupby(col).left.agg(employees='size', leavers='sum', attrition_rate='mean')
        table.to_csv(OUT/f'attrition_by_{col}.csv'); tables[col]=table
    fig, axes = plt.subplots(1,2,figsize=(12,4))
    for ax,col in zip(axes,['department','salary']):
        t=tables[col].sort_values('attrition_rate')
        ax.barh(t.index.astype(str),t.attrition_rate*100,color='#167d9a')
        ax.set_xlabel('Observed attrition (%)'); ax.set_title(f'Attrition by {col}')
    fig.tight_layout(); fig.savefig(FIG/'attrition_groups.png',dpi=160); plt.close(fig)
    fig, axes = plt.subplots(1,2,figsize=(11,4))
    for label,color in [(0,'#167d9a'),(1,'#dd7846')]:
        part=df[df.left==label]
        for ax,col in zip(axes,['satisfaction_level','average_monthly_hours']):
            ax.hist(part[col],bins=25,density=True,alpha=.5,label='Left' if label else 'Stayed',color=color)
            ax.set_xlabel(col.replace('_',' ').title()); ax.set_ylabel('Density'); ax.legend()
    fig.tight_layout();fig.savefig(FIG/'workload_satisfaction.png',dpi=160);plt.close(fig)
    print('Group-level tables and exploratory figures saved.')
    return tables

def scores(y,p):
    pred=p>=.5
    return { 'accuracy':float(accuracy_score(y,pred)), 'precision':float(precision_score(y,pred,zero_division=0)),
        'recall':float(recall_score(y,pred,zero_division=0)), 'f1':float(f1_score(y,pred,zero_division=0)),
        'roc_auc':float(roc_auc_score(y,p)), 'average_precision':float(average_precision_score(y,p))}

def train_models(df):
    X=df.drop(columns='left'); y=df.left
    X_dev,X_test,y_dev,y_test=train_test_split(X,y,test_size=.2,stratify=y,random_state=SEED)
    X_train,X_val,y_train,y_val=train_test_split(X_dev,y_dev,test_size=.25,stratify=y_dev,random_state=SEED)
    num=X.select_dtypes(include='number').columns.tolist(); cat=X.select_dtypes(exclude='number').columns.tolist()
    def preprocess():
        return ColumnTransformer([('num',Pipeline([('impute',SimpleImputer(strategy='median')),('scale',StandardScaler())]),num),
            ('cat',Pipeline([('impute',SimpleImputer(strategy='most_frequent')),('encode',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),cat)])
    candidates={'Dummy baseline':DummyClassifier(strategy='prior'),
        'Logistic regression':LogisticRegression(max_iter=2000,random_state=SEED),
        'Decision tree':DecisionTreeClassifier(max_depth=6,min_samples_leaf=20,random_state=SEED),
        'Random forest':RandomForestClassifier(n_estimators=200,max_depth=12,min_samples_leaf=3,n_jobs=2,random_state=SEED)}
    rows=[]; models={}
    for name,est in candidates.items():
        model=Pipeline([('prepare',preprocess()),('classifier',est)])
        model.fit(X_train,y_train); models[name]=model
        row={'model':name,**scores(y_val,model.predict_proba(X_val)[:,1])};rows.append(row)
        print(name, row,flush=True)
    comparison=pd.DataFrame(rows).sort_values('average_precision',ascending=False)
    comparison.to_csv(OUT/'validation_metrics.csv',index=False)
    winner=comparison.iloc[0]['model']; model=models[winner]
    importance=permutation_importance(model,X_val,y_val,scoring='average_precision',n_repeats=5,random_state=SEED,n_jobs=2)
    imp=pd.DataFrame({'feature':X.columns,'mean_ap_decrease':importance.importances_mean,'std':importance.importances_std}).sort_values('mean_ap_decrease',ascending=False)
    imp.to_csv(OUT/'feature_importance.csv',index=False)
    fig,ax=plt.subplots(figsize=(8,5));s=imp.sort_values('mean_ap_decrease');ax.barh(s.feature,s.mean_ap_decrease,xerr=s['std'],color='#167d9a')
    ax.set_xlabel('Validation average precision decrease after permutation');fig.tight_layout();fig.savefig(FIG/'feature_importance.png',dpi=160);plt.close(fig)
    # Select on validation only, refit on development data, then evaluate held-out test once.
    model.fit(X_dev,y_dev); p=model.predict_proba(X_test)[:,1]; metrics=scores(y_test,p)
    cm=confusion_matrix(y_test,p>=.5,labels=[0,1])
    fig,ax=plt.subplots(figsize=(5,4));ConfusionMatrixDisplay(cm,display_labels=['Stayed','Left']).plot(ax=ax,colorbar=False,cmap='Blues');fig.tight_layout();fig.savefig(FIG/'confusion_matrix.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(6,4));PrecisionRecallDisplay.from_predictions(y_test,p,ax=ax,name=winner);ax.axhline(y_test.mean(),ls='--',label='Test prevalence');ax.legend();fig.tight_layout();fig.savefig(FIG/'precision_recall.png',dpi=160);plt.close(fig)
    # Bootstrap uncertainty for fixed test predictions; does not include training uncertainty.
    rng=np.random.default_rng(SEED); yt=y_test.to_numpy(); aps=[]
    for _ in range(500):
        idx=rng.integers(0,len(yt),len(yt))
        if len(np.unique(yt[idx]))==2: aps.append(average_precision_score(yt[idx],p[idx]))
    result={'selected_model':winner,'threshold':.5,'split':{'train':len(X_train),'validation':len(X_val),'test':len(X_test)},
        'test_metrics':metrics,'confusion_matrix':cm.tolist(),'test_prevalence':float(y_test.mean()),
        'test_ap_bootstrap_95_ci':np.quantile(aps,[.025,.975]).tolist(),'seed':SEED}
    (OUT/'model_results.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
    return result, comparison, imp

def main():
    df,audit=load_data(); explore(df); train_models(df)
if __name__=='__main__': main()
