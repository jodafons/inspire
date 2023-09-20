import numpy as np
import pandas as pd
import bibtexparser, arxiv
import os, copy

from tqdm import tqdm
from loguru import logger
from copy import copy

class bibtex_extractor:
    
    def __init__(self, inspire_path: str, me: str, collaboration: str):
        
        self.me = me
        self.collaboration = collaboration
        self.inspire_path = inspire_path
        with open(inspire_path,'r') as f:
            logger.info(f"Reading inspire bibtex from {inspire_path}")
            self.database = bibtexparser.load(f)
                    
        
    def extract(self):

        logger.info("Extracting all information from bibtex file...")
        self.df = pd.DataFrame(self.database.entries)
        
        
    def apply_qualis( self , qualis ):
        
        logger.info("Applying qualis from CAPES...")
        def apply_qualis(qualis, row):
            return qualis[row.journal][1] if row.journal in qualis.keys() else np.nan
            
        def apply_journal_name(qualis, row):
            return qualis[row.journal][0] if row.journal in qualis.keys() else np.nan

        def apply_keywords(me, collaboration, row):
            author = me if me in row.author else collaboration   
            return row.qualis+','+author if type(row.qualis) is str else author
        self.df['qualis']       = self.df.apply( lambda row: apply_qualis(qualis, row), axis='columns' )
        self.df['journal_name'] = self.df.apply( lambda row: apply_journal_name(qualis, row), axis='columns' )
        self.df['keywords']     = self.df.apply( lambda row: apply_keywords(self.me, self.collaboration, row), axis='columns' )
        self.df = self.df[self.df['qualis'].notna()]
        
        
    def dump(self, output):
        
        papers = []
        database = copy(self.database)
        for idx, paper in tqdm( enumerate(database.entries), desc='dumping...', total=len(database.entries)):
            entry = copy(paper)
            paper_id = paper['ID']
            keywords = self.df.loc[self.df['ID']==paper_id].keywords.values
            if len(keywords) > 0:
                paper['keywords'] = keywords[0]
                papers.append(paper)
        
        database.entries = papers
        logger.info(f"Saving bibtex to {output}")
        with open(output,'w') as f:
            bibtexparser.dump(database,f)



        