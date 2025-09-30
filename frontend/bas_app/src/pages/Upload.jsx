import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import { CloudArrowUpIcon, DocumentTextIcon, TableCellsIcon } from '@heroicons/react/24/outline';
import api from '../services/api';

const Upload = () => {
  const [uploading, setUploading] = useState(false);
  const [uploadHistory, setUploadHistory] = useState([]);

  const handleUpload = async (files, type) => {
    setUploading(true);
    const formData = new FormData();
    formData.append('file', files[0]);

    try {
      const endpoint = type === 'excel' ? '/flights/upload/excel' : '/flights/upload/shr';
      const response = await api.post(endpoint, formData);
      
      toast.success(`Успешно обработано: ${response.data.processed} записей`);
      
      setUploadHistory(prev => [{
        id: Date.now(),
        filename: files[0].name,
        type,
        processed: response.data.processed,
        timestamp: new Date().toISOString(),
        status: 'success'
      }, ...prev]);
    } catch (error) {
      toast.error('Ошибка при загрузке файла');
      console.error(error);
    } finally {
      setUploading(false);
    }
  };

  const ExcelDropzone = () => {
    const onDrop = useCallback((acceptedFiles) => {
      handleUpload(acceptedFiles, 'excel');
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
      onDrop,
      accept: {
        'application/vnd.ms-excel': ['.xls'],
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
      },
      maxFiles: 1
    });

    return (
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <TableCellsIcon className="mx-auto h-12 w-12 text-gray-400" />
        <p className="mt-2 text-sm font-medium text-gray-900">Excel файлы</p>
        <p className="mt-1 text-xs text-gray-500">XLS, XLSX с данными о полетах</p>
        {isDragActive ? (
          <p className="mt-2 text-sm text-blue-600">Отпустите файл здесь...</p>
        ) : (
          <button className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm">
            Выбрать файл
          </button>
        )}
      </div>
    );
  };

  const SHRDropzone = () => {
    const onDrop = useCallback((acceptedFiles) => {
      handleUpload(acceptedFiles, 'shr');
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
      onDrop,
      accept: {
        'application/json': ['.json'],
        'application/xml': ['.xml'],
        'text/plain': ['.txt']
      },
      maxFiles: 1
    });

    return (
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive ? 'border-green-500 bg-green-50' : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
        <p className="mt-2 text-sm font-medium text-gray-900">SHR телеграммы</p>
        <p className="mt-1 text-xs text-gray-500">JSON, XML, TXT с SHR сообщениями</p>
        {isDragActive ? (
          <p className="mt-2 text-sm text-green-600">Отпустите файл здесь...</p>
        ) : (
          <button className="mt-4 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm">
            Выбрать файл
          </button>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Загрузка данных</h2>
        <p className="mt-1 text-sm text-gray-600">
          Загрузите файлы с полетными данными для анализа
        </p>
      </div>

      {uploading && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center">
            <CloudArrowUpIcon className="h-5 w-5 text-blue-600 mr-2 animate-pulse" />
            <span className="text-sm text-blue-700">Обработка файла...</span>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <ExcelDropzone />
        <SHRDropzone />
      </div>

      {/* История загрузок */}
      {uploadHistory.length > 0 && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">История загрузок</h3>
          </div>
          <ul className="divide-y divide-gray-200">
            {uploadHistory.map((item) => (
              <li key={item.id} className="px-4 py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{item.filename}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(item.timestamp).toLocaleString('ru-RU')}
                    </p>
                  </div>
                  <div className="flex items-center">
                    <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                      {item.processed} записей
                    </span>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default Upload;