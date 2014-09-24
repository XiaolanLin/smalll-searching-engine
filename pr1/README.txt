This project is about to generate an indexer for the given web documents.

To run my program, you need to :

1). install the nltk package.

2). install the beautiful soup

3). there are three py files in my program

	tokenizer.py: run this file with command : python tokenizer.py corpus 
				[the corpus should be in the same folder with tokenizer.py]
				implement the Part I. To tokenize the documents in the corpus directory.

				[extra credit attempt]
				My program wil run in constant memory with respect to the number of documents
				and the length of a document. 
				When tokenizing 400 docs, the memory usage is 329,543,680 bytes
				When tokenizing 800 docs. the memory usage is 204,742,656 bytes
				When tokenizing 3200 docs. the memory usage is 331,636,736 bytes
				According to the experiment results, that when the number of documents go up, the memory
				is similar when the doc number is 400 up to 3200

	invert_index.py: reads the doc_index.txt and constructs an inverted index.
				run this file with: python inver_index.py 
				implement Part II. Construct the term_index.txt file and term_info.txt file

				[extra credit attempt]
				My progrm will run in constant memory with respect to the number of documents and term positions
				My program run in linear time with respect to the length of doc_index.txt and using constant
				memory with respect to the number of documents, term posiitons, and terms.
				when doc_index.txt is 39855 lines, number of doc = 100, number of terms = 14526
				memory usage is 26,247,168	running time = 0.7s
				When doc_index.txt = 170152 lines, number of doc = 400, number of terms = 31184
				memory usage is 110,596,096	running time = 3.65s
				When doc_index.txt = 338730 lines, number of doc = 800, number of terms = 70554
				memory usage is 216,432,640	running time = 7.67s
				When doc_index.txt = 1330874 lines, number of doc = 3200, number of terms = 167809
				memory usage is 694,456,320	running time = 24.9s
				[extra credit attempt]
				According to my experiment results, the runtime is linear with respect to the length of the input file. and the 

	read_index.py: implement the Part 3
				 the tool which reads the index and prints information read from it

4). all the generated files are saved in the output.zip including:
	docids.txt
	termids.txt
	doc_index.txt
	term_index.txt
	term_info.txt