import React, { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';

interface DocumentRefreshContextType {
  refreshCount: number;
  triggerRefresh: () => void;
}

const DocumentRefreshContext = createContext<DocumentRefreshContextType | undefined>(undefined);

export const useDocumentRefresh = () => {
  const context = useContext(DocumentRefreshContext);
  if (context === undefined) {
    throw new Error('useDocumentRefresh must be used within a DocumentRefreshProvider');
  }
  return context;
};

export const DocumentRefreshProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [refreshCount, setRefreshCount] = useState(0);

  const triggerRefresh = () => setRefreshCount((c) => c + 1);

  return (
    <DocumentRefreshContext.Provider value={{ refreshCount, triggerRefresh }}>
      {children}
    </DocumentRefreshContext.Provider>
  );
}; 