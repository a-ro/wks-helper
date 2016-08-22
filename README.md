# Watson Knowledge Studio Helper
Use the import-export functionality of Watson Knowledge Studio (WKS) to modify sets and documents in a way that is not possible with the WKS interface. This project was created in response to this dwanswer [post][1] about removing documents from a task in progress without losing the annotations. 

## Removing documents from a set already in progress without losing the annotations
These steps assume that you want to separate the documents that were annotated (status "in progress / completed") from the other documents in the set. You might skip some of these if that's not the case, but I strongly recommend to follow this if you would like to train a machine learning annotator on the documents that were already annotated:

1. Go in the "documents" tab of Watson Knowledge Studio (WKS) and click on the "export" button. This will download a zip folder that contains your corpus. Note that for your set in progress, the annotations have not yet been applied as you need to have all documents completed and approved for the annotations to be saved. 
2. Find the id of your set by opening the "sets.json" file in your exported corpus. Be careful as multiple sets can have the same name.
3. Find the ids of all documents that are "in progress" or "completed" in the set that you want to modify. I don't think this can be achieved automatically as the "modifiedDate" of the documents correspond to the date at which they were created, and their "status" are all the same. You can use my helper function to generate a csv with the ids and names of the documents in the selected set. This will create an additional column "isModified" of values=0 that you can manually set to 1 by verifying the status of each document in WKS. 

 ```python
         from document_filtering import generate_document_csv
         generate_document_csv('/path/to/corpus-directory', 
                               document_set_id='abcdefg7-4215-8528-a5d5273c4b')
 ```

4. Ask your annotators to change the status of all documents in your set to "completed".
5. Resolve any conflicts and Approve the annotations.
6. Go in the "documents" tab of Watson Knowledge Studio (WKS) and click on the "export" button (now we have the documents and their annotations).
7.  Create a new corpus with the documents that were 'in progress/completed'. You can call the following function in my code and send it the path of the csv that was created at step 3.  If you don't delete the set with id=document_set_id from Watson Knowledge Studio, the ids of the documents must be modified. Otherwise, Watson Knowledge Studio will throw an error when importing your new corpus because of the id duplication. As a workaround I used the id_prefix to specify a prefix that will be appended to the id of all documents.

 ```python
         from document_filtering import create_new_corpus_with_selected_documents
         create_new_corpus_with_selected_documents(corpus_directory_path='/path/to/corpus-directory',
                                                   document_set_id='abcdefg7-4215-8528-a5d5273c4b',
                                                   id_prefix='unique-id-prefix',
                                                   save_directory_path='/path/to/new/corpus-directory',
                                                   csv_file_path='modified-documents.csv')
  ```
  
8. Import your new corpus in WKS. This corpus will contains only the documents in your set that were "in progress/completed".

9. Import the documents that were not "in progress/completed". These documents don't have any annotations, so you can just delete the documents "in progress/completed" from your original directory of text files that you uploaded in WKS. You can then upload the remaining documents. Make sure to make smaller sets so you don't have to follow all these steps EVER again ;)  


  [1]: https://developer.ibm.com/answers/questions/296585/watson-knowledge-studio-deleting-documents-from-a.html



