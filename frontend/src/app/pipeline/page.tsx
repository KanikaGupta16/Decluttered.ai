'use client';

import PipelineUpload from '@/components/PipelineUpload';

export default function PipelinePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
      <div className="container mx-auto py-8">
        <PipelineUpload />
      </div>
    </div>
  );
}