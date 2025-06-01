export async function analyzeVideo({
  videoUrl,
  modelName,
  mode
}: {
  videoUrl: string;
  modelName: string;
  mode: string;
}) {
  const response = await fetch('http://localhost:8000/api/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      video_url: videoUrl,
      model_name: modelName,
      mode
    })
  });
  if (!response.ok) throw new Error('Failed to analyze video');
  return response.json();
} 