Converting codebases to a single text file for long context LLMs

## Usage

# ignore .py, inlcude src and test folders
 repo_to_text -r jkorsvik/NMBUFlowTorch -i .py -d src test -o flowtorch_prompt.txt 

 repo_to_text -r langchain-ai/langchain -o langchain_prompt.txt