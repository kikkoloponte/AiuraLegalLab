"""
Configurazione condivisa della suite.

AIURA_FULLTEXT_CONTEXT=0: i test non devono toccare il MongoDB reale
attraverso il fetch del testo pieno (source_texts) innescato da
orchestrator/analyst. I test dedicati riattivano il flag con
monkeypatch.setenv e iniettano un database mongomock.
"""
import os

os.environ.setdefault("AIURA_FULLTEXT_CONTEXT", "0")
