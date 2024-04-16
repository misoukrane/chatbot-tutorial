# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import uuid
from itemadapter import ItemAdapter
from bs4 import BeautifulSoup
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from openai import OpenAI
from qdrant_client import models, QdrantClient


class CodereliantPipeline:
    def process_item(self, item, spider):
        return item


class BodyTxtConverterPipeline:
    # use beautifulsoup to convert html to text
    def process_item(self, item, spider):
        item['plain_body'] = BeautifulSoup(
            item['body'], 'html.parser').get_text()
        return item


class TextSplitterPipeline:
    def open_spider(self, spider):
        self.text_splitter = SemanticChunker(
            OpenAIEmbeddings(), breakpoint_threshold_type="percentile"
        )

    def process_item(self, item, spider):
        docs = self.text_splitter.create_documents([item['plain_body']])
        item['chunks'] = []
        for doc in docs:
            text = doc.page_content.replace("\n", " ")
            item['chunks'].append(text)
        return item

class VecorDBPipeline:
    def open_spider(self, spider):
        # constants
        self.COLLECTION_NAME = "codereliant"
        self.EMBEDDING_MODEL = "text-embedding-3-small"
        self.EMBEDDING_MODEL_VECOTR_SIZE = 1536 # hardcoded, but can be obtained from the model

        # clients
        self.openai_client = OpenAI()
        self.client = QdrantClient(url="http://localhost:6333")

        # create collection in qdrant
        self.client.recreate_collection(
            collection_name=self.COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=self.EMBEDDING_MODEL_VECOTR_SIZE,  
                distance=models.Distance.COSINE,
            ),
        )

    def process_item(self, item, spider):
        unique_ids = [str(uuid.uuid4()) for _ in item['chunks']]
        result = self.openai_client.embeddings.create(input=item["chunks"], model=self.EMBEDDING_MODEL)

        self.client.upload_points(
            collection_name=self.COLLECTION_NAME,
            points=[
                models.PointStruct(
                    id=unique_id,
                    vector=data.embedding,
                    payload={
                        "url": item['url'],
                        "title": item['title'],
                        "description": item['description'],
                        "chunk": chunk,
                    }
                )
                for unique_id, chunk, data in zip(unique_ids, item['chunks'], result.data)
            ],
        )
        return item
