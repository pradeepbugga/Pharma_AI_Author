# AI-Assisted IND Authoring from Scientific Papers

**An agentic LLM system that converts unstructured biomedical literature into structured, verified fields for generation of an IND filing introductory section**

### Goal 
Traditional LLM pipelines fail in regulated domains like pharma because they generate text without grounding in verifiable sources (i.e. hallucination).  In this project, I generate accurate outputs by combining 
structured extraction with cross-validation against established scientific databases.  

### Demo
You can try this project out at http://ind.nihaudit.com.  This demo starts with a preclinical KRAS paper (MRTX1133 by Mirati Therapuetics), performs structured extraction of fields (results shown in right pane), then displays 
the synthesized LLM IND introductory text in the bottom panel.  Importantly, you can click on each of the extracted fields to open up a modal with corresponding source evidence.

### System Overview 

Below is a high-level overview of our approach to AI authoring for pharma regulatory text. 
- We first decompose the official IND introduction guidelines into fields (i.e. primary drug, class, dose, etc.).  
- Next, we hierarchically build each of those fields from the source publication
- We start with primary drug, which involves using biomedical named entity extraction (NER) to get all the named entities in the text.  We then feed each of those names to database APIs for compounds (PubChem), proteins/genes (UniProt), and cell lines (Cellosaurus), then use an LLM to identify the primary drug (with additional assistance from web search).
- With the primary drug identified, we then use that ground truth to incrementally identify more fields from the text
- Finally, with all fields identified, we use an LLM to generate text exclusively from those fields (rather than the full initial source text)

![Alt Text](/excalidraw_overview.svg)

### Practical Benefits

- Our approach will  provide both high accuracy text generation and high traceability (corresponding evidence for each extraction decision).  You can confirm for yourself that evidence provided in the pop-up/ modal indeed corresponds to text from the source publication verbatim
- This approach will also save significant time in IND filing drafting as a variety of input sources (publications, internal data, etc.) can be included and an LLM can reason across each of the sources
- We also intentionally chose Kimi K2 because this model is fast, efficient, and open-source, enabling straightforward adoption by pharmaceutical companies without concern for unintentional IP disclosure to LLM vendors

### Limitations

- I restricted myself to a single preclinical paper to demonstrate proof-of-concept.  In practice, a variety of input data sources will be included.
- I did not automate the initial ingest / parsing portion of input paper.  Considering I have prior experience with parsing papers (see https://github.com/pradeepbugga/Med_Chem_Search), I deprioritized this part.
- The latency is roughly 4-5 minutes for the entire process.  GPU acceleration shaves off 20-30 seconds for the intial NER step, but the rate-limiting step is actually the entity classification (i.e. looping through each named entity and identifying it as drug/protein/gene/cell line/other.  On the flip side, having this information could be valuable for drafting other types of documents (i.e. those that require details on in vitro experiments).
- Our workflows are not entirely agentic nor autonomous as as deterministically go through each database API step by step, use web search as a fallback, then send that information to an LLM.  The purely agentic alternative would use those database APIs as tools and reason through each appropriately for an answer.  Ultimately, I found that the approach I used here was providing high quality results and therefore I left the architecture as is.
- The IND introduction is only a few sentences and does not include information that mainly pertains to pharmacology, toxicology, and investigational study plans.  The same approach of structured field extraction and synthesis can be used for these sections as long as we have input text that covers this information (this preclinical paper naturally did not).

### Setup 
#### Prerequisites 
Python 3.10+ (I used 3.14.3)
React (frontend)
API keys for Tavily (web search API) and Kimi K2 (Moonshot AI LLM API) 

#### Environment Setup
```
git clone https://github.com/pradeepbugga/Pharma_AI_Author.git
cd Pharma_AI_Author
```
```
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```
#### Environment Variables
```
KIMI_K_API_KEY = ...
TAVILY_API_KEY = ...
```
(no API key used for PubChem, Cellosaurus, and UniProt)

### Next Steps
   The immediate steps are to test on a variety of other input scientific papers to confirm that our approach is generalizable and not overfitting to this specific paper.  After that, we can expand from just the introductory section of the IND filing to other sections. 




