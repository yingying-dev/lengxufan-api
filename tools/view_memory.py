"""ChromaDB数据可视化工具 - 查看存储的记忆条目"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import chromadb

def main():
    keyword = sys.argv[1] if len(sys.argv) > 1 else None
    client = chromadb.PersistentClient(path="data/chroma_db")
    try:
        collection = client.get_collection("episodic_memories")
        results = collection.get()
        if results and results["documents"]:
            print(f"共 {len(results['documents'])} 条记忆：\n")
            for i, (doc_id, doc) in enumerate(zip(results["ids"], results["documents"]), 1):
                if keyword and keyword not in doc:
                    continue
                print(f"[{i}] {doc}")
        else:
            print("数据库中暂无记忆条目。")
    except Exception as e:
        print(f"读取失败: {e}")

if __name__ == "__main__":
    main()