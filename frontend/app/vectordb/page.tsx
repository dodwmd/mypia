'use client';
import React from 'react';
import VectorDbQuerier from '../../src/components/vectordb/VectorDbQuerier';
import VectorDbAdder from '../../src/components/vectordb/VectorDbAdder';

export default function VectorDbPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">Vector Database</h1>
      <VectorDbAdder />
      <VectorDbQuerier />
    </div>
  );
}
