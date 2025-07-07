import { useMutation } from '@tanstack/react-query';
import { uploadCsvFile, querySpreadsheet } from '../api/spreadsheetApi';

// Upload mutation hook
export const useUploadCsv = () => {
  return useMutation({
    mutationFn: uploadCsvFile,
    onSuccess: (data) => {
      console.log('Upload successful:', data);
    },
    onError: (error) => {
      console.error('Upload failed:', error);
    },
  });
};

// Query mutation hook with optimistic updates
export const useQuerySpreadsheet = () => {
  return useMutation({
    mutationFn: querySpreadsheet,
    onSuccess: (data) => {
      console.log('Query successful:', data);
    },
    onError: (error) => {
      console.error('Query failed:', error);
    },
  });
};

// Query key factories for better cache management
export const spreadsheetKeys = {
  all: ['spreadsheet'] as const,
  uploads: () => [...spreadsheetKeys.all, 'uploads'] as const,
  upload: (filename: string) => [...spreadsheetKeys.uploads(), filename] as const,
  queries: () => [...spreadsheetKeys.all, 'queries'] as const,
  query: (question: string) => [...spreadsheetKeys.queries(), question] as const,
};