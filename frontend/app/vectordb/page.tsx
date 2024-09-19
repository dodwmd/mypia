'use client';
import React from 'react';
import VectorDbAdder from '../../src/components/vectordb/VectorDbAdder';
import VectorDbQuery from '../../src/components/vectordb/VectorDbQuery';

const VectorDbPage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Vector Database Management</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <VectorDbAdder />
        <VectorDbQuery />
      </div>
    </div>
  );
};

export default VectorDbPage;
