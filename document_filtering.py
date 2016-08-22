__author__ = 'amelie'

import json
import os
from os.path import join
import errno

import pandas
import numpy


def generate_document_csv(corpus_directory_path, document_set_id, csv_save_path='corpus.csv'):
    """Generate a csv with the ids and names of the documents in the selected document set
       and add a column "isModified" of values=0

    Args:
        corpus_directory_path (str): Path of the corpus that was exported with Watson Knowledge Studio.
        document_set_id (str): Id of the document set (open the documents.json file to find the id of your set)
        csv_save_path (str): Save path of the csv file

    """
    documents_in_set = _find_documents_in_set(corpus_directory_path, document_set_id)
    document_ids, document_names = _get_document_ids_and_names(corpus_directory_path, documents_in_set)
    is_modified = [0] * len(document_ids)
    dataframe = pandas.DataFrame(data={'id': document_ids, 'name': document_names, 'isModified': is_modified})
    dataframe.sort_values(by='name', inplace=True)
    dataframe.to_csv(csv_save_path)


def _find_documents_in_set(corpus_directory_path, document_set_id):
    sets_file_path = join(corpus_directory_path, 'sets.json')
    document_set = _get_set(sets_file_path, document_set_id)
    return document_set['documents']


def _load_json(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data


def _get_set(sets_file_path, document_set_id):
    sets = _load_json(sets_file_path)
    for document_set in sets:
        if document_set['id'] == document_set_id:
            return document_set
    raise ValueError('document set with id {} was not found'.format(document_set_id))


def _get_document_ids_and_names(corpus_directory_path, documents_in_set):
    document_ids = []
    document_names = []
    for document_id in documents_in_set:
        document_path = join(corpus_directory_path, 'gt', '{}.json'.format(document_id))
        with open(document_path, 'r') as json_file:
            data = json.load(json_file)
            document_ids.append(data['id'])
            document_names.append(data['name'])
    return document_ids, document_names


def create_new_corpus_with_selected_documents(corpus_directory_path, document_set_id, id_prefix, save_directory_path,
                                              csv_file_path='corpus.csv'):
    """Create a new Watson Knowledge Studio corpus with the selected documents of the set.
       The selected documents must have the value isModified=1 in the csv_file.

       If you don't delete the set with id=document_set_id from Watson Knowledge Studio, the ids of the documents
       must be modified. Otherwise, Watson Knowledge Studio will throw an error when importing your new corpus
       because of the id duplication. Use the id_prefix to specify a prefix that will be appended to the id of all
       documents.

    Args:
        corpus_directory_path (str): Path of the corpus that was exported with Watson Knowledge Studio.
        document_set_id (str): Id of the document set (open the documents.json file to find the id of your set)
        id_prefix (str): Prefix that will be appended to all document ids to avoid WKS import error
        save_directory_path (str): Path of the directory where the new corpus will be saved
        csv_file_path (str): Path of the csv file
    """
    document_ids = _get_selected_document_ids(csv_file_path)
    print('{:d} documents were selected.'.format(len(document_ids)))
    _save_modified_set(corpus_directory_path, document_set_id, document_ids, id_prefix, save_directory_path)
    _save_modified_documents(corpus_directory_path, document_ids, id_prefix, save_directory_path)
    _save_ground_truth(corpus_directory_path, id_prefix, document_ids, save_directory_path)


def _get_selected_document_ids(csv_file_path):
    dataframe = pandas.read_csv(csv_file_path)
    selected_documents = dataframe[dataframe['isModified'] == True]
    document_ids = selected_documents['id'].values
    return document_ids


def _save_modified_set(corpus_directory_path, document_set_id, document_ids, id_prefix, save_directory_path):
    sets_file_path = join(corpus_directory_path, 'sets.json')
    document_set = _get_set(sets_file_path, document_set_id)
    selected_document_ids_with_prefix = ['{}-{}'.format(id_prefix, document_id) for document_id in document_ids]
    document_set['id'] = '{}-{}'.format(id_prefix, document_set['id'])
    document_set['documents'] = selected_document_ids_with_prefix
    document_set['count'] = len(document_ids)
    sets_new_path = join(save_directory_path, 'sets.json')
    _save_json(sets_new_path, [document_set])


def _save_modified_documents(corpus_directory_path, document_ids, id_prefix, save_directory_path):
    documents = _load_json(join(corpus_directory_path, 'documents.json'))
    selected_document_indexes = []
    for index, document in enumerate(documents):
        if document['id'] in document_ids:
            selected_document_indexes.append(index)
            document['id'] = '{}-{}'.format(id_prefix, document['id'])
    documents = list(numpy.array(documents)[selected_document_indexes])
    documents_new_path = join(save_directory_path, 'documents.json')
    _save_json(documents_new_path, documents)


def _save_ground_truth(corpus_directory_path, id_prefix, document_ids, save_directory_path):
    new_ground_truth_path = join(save_directory_path, 'gt')
    if not os.path.exists(new_ground_truth_path):
        os.makedirs(new_ground_truth_path)
    for document_id in document_ids:
        document_path = join(corpus_directory_path, 'gt', '{}.json'.format(document_id))
        document_annotations = _load_json(document_path)
        document_annotations['id'] = '{}-{}'.format(id_prefix, document_annotations['id'])
        new_document_path = join(new_ground_truth_path, '{}.json'.format(document_annotations['id']))
        _save_json(new_document_path, document_annotations)


def _save_json(file_path, data):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file)


def delete_selected_documents_from_directory(directory_path, csv_file_path):
    """Delete selected documents from a directory.
       The selected documents must have the value isModified=1 in the csv_file.
       The documents in the directory must have the same name as in the csv "name" column.

    Args:
        directory_path (str): Path of the directory where the files to delete are found.
        csv_file_path (str): Path of the csv file.
    """
    dataframe = pandas.read_csv(csv_file_path)
    selected_documents = dataframe[dataframe['isModified'] == True]
    deleted_count = 0
    for name in selected_documents['name']:
        try:
            os.remove(join(directory_path, name))
            deleted_count += 1
        except FileNotFoundError as exception:
            print(exception)
    print('{:d} documents were deleted.'.format(deleted_count))