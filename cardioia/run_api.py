def main():
    import uvicorn
    uvicorn.run("cardioia.api:app",host="0.0.0.0",port=8000,reload=False)
if __name__=="__main__":main()
