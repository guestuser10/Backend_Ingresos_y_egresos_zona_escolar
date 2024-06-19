from pydantic import BaseModel

class PDFBase(BaseModel):

    doc_name: str
    school: str
    start_year: str
    end_year: str
    
class PDFCreate(PDFBase):
    
    pass