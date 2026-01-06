import { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { signingService, SigningTokenInfo } from '../services/signing';

type SigningStep = 'loading' | 'error' | 'review' | 'sign' | 'success';

export default function SignDocument() {
  const { token } = useParams<{ token: string }>();
  const [step, setStep] = useState<SigningStep>('loading');
  const [tokenInfo, setTokenInfo] = useState<SigningTokenInfo | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [hasReadDocument, setHasReadDocument] = useState(false);
  const [signatureData, setSignatureData] = useState<string | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);

  useEffect(() => {
    if (token) {
      validateToken();
    }
  }, [token]);

  const validateToken = async () => {
    try {
      setError(null);
      const info = await signingService.validateToken(token!);
      setTokenInfo(info);
      setStep('review');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid or expired signing link');
      setStep('error');
    }
  };

  const handleStartSigning = () => {
    if (!hasReadDocument) {
      setError('Please confirm that you have read and understood the document');
      return;
    }
    setStep('sign');
  };

  const startDrawing = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current) return;
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    setIsDrawing(true);
    ctx.beginPath();
    ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top);
  };

  const draw = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.lineTo(e.clientX - rect.left, e.clientY - rect.top);
    ctx.strokeStyle = '#000';
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.stroke();
  };

  const stopDrawing = () => {
    setIsDrawing(false);
    if (canvasRef.current) {
      const dataUrl = canvasRef.current.toDataURL('image/png');
      setSignatureData(dataUrl);
    }
  };

  const clearSignature = () => {
    if (canvasRef.current) {
      const ctx = canvasRef.current.getContext('2d');
      if (ctx) {
        ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
      }
      setSignatureData(null);
    }
  };

  const handleSubmitSignature = async () => {
    if (!signatureData || !token) {
      setError('Please provide your signature');
      return;
    }

    try {
      setError(null);
      await signingService.signDocument(token, signatureData);
      setStep('success');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit signature');
    }
  };

  if (step === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Validating signing link...</p>
        </div>
      </div>
    );
  }

  if (step === 'error') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="text-6xl mb-4">❌</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Invalid Signing Link</h1>
          <p className="text-gray-600 mb-6">{error}</p>
          <p className="text-sm text-gray-500">
            Please contact your agent or project manager for a new signing link.
          </p>
        </div>
      </div>
    );
  }

  if (step === 'success') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="text-6xl mb-4">✅</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Signature Submitted Successfully</h1>
          <p className="text-gray-600 mb-4">
            Your signature has been submitted and is pending manager approval.
          </p>
          <p className="text-sm text-gray-500 mb-6">
            You will receive confirmation via email/SMS once your signature is approved.
          </p>
          <div className="bg-teal-50 border border-teal-200 rounded-lg p-4 text-left">
            <p className="text-sm text-teal-800">
              <strong>Next Steps:</strong>
            </p>
            <ul className="text-sm text-teal-700 mt-2 space-y-1 list-disc list-inside">
              <li>Your signature is being reviewed by the project manager</li>
              <li>You will be notified once approval is complete</li>
              <li>If you have questions, please contact your agent</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  if (step === 'review' && tokenInfo) {
    return (
      <div className="min-h-screen bg-gray-50 py-8 px-4">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Document Signing</h1>
            <p className="text-gray-600">
              Please review the document below before signing
            </p>
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong>Document:</strong> {tokenInfo.document_name}
              </p>
              <p className="text-sm text-blue-800 mt-1">
                <strong>Owner:</strong> {tokenInfo.owner_name}
              </p>
            </div>
          </div>

          {/* Document Preview Placeholder */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Document Preview</h2>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center bg-gray-50">
              <div className="text-4xl mb-4">📄</div>
              <p className="text-gray-600 mb-2">Document: {tokenInfo.document_name}</p>
              <p className="text-sm text-gray-500">
                In Phase 2, this will display the actual PDF document
              </p>
              <p className="text-sm text-gray-500 mt-4">
                <a
                  href={`/api/v1/files/${tokenInfo.document_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-teal-600 hover:text-teal-700 underline"
                >
                  View Document (if available)
                </a>
              </p>
            </div>
          </div>

          {/* Confirmation */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
            <label className="flex items-start cursor-pointer">
              <input
                type="checkbox"
                checked={hasReadDocument}
                onChange={(e) => setHasReadDocument(e.target.checked)}
                className="mt-1 mr-3 h-5 w-5 text-teal-600 border-gray-300 rounded focus:ring-teal-500"
              />
              <span className="text-gray-700">
                I confirm that I have read and understood the document above, and I agree to sign it.
              </span>
            </label>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
              {error}
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end gap-4">
            <button
              onClick={handleStartSigning}
              disabled={!hasReadDocument}
              className="px-6 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              Continue to Sign
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (step === 'sign' && tokenInfo) {
    return (
      <div className="min-h-screen bg-gray-50 py-8 px-4">
        <div className="max-w-2xl mx-auto">
          {/* Header */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Sign Document</h1>
            <p className="text-gray-600">
              Please sign below using your mouse or touch screen
            </p>
          </div>

          {/* Signature Canvas */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Your Signature</h2>
            <div className="border-2 border-gray-300 rounded-lg bg-white">
              <canvas
                ref={canvasRef}
                width={600}
                height={200}
                className="w-full cursor-crosshair touch-none"
                onMouseDown={startDrawing}
                onMouseMove={draw}
                onMouseUp={stopDrawing}
                onMouseLeave={stopDrawing}
                onTouchStart={(e) => {
                  e.preventDefault();
                  const touch = e.touches[0];
                  const mouseEvent = new MouseEvent('mousedown', {
                    clientX: touch.clientX,
                    clientY: touch.clientY,
                  });
                  canvasRef.current?.dispatchEvent(mouseEvent);
                }}
                onTouchMove={(e) => {
                  e.preventDefault();
                  const touch = e.touches[0];
                  const mouseEvent = new MouseEvent('mousemove', {
                    clientX: touch.clientX,
                    clientY: touch.clientY,
                  });
                  canvasRef.current?.dispatchEvent(mouseEvent);
                }}
                onTouchEnd={(e) => {
                  e.preventDefault();
                  stopDrawing();
                }}
              />
            </div>
            <div className="mt-4 flex justify-end">
              <button
                onClick={clearSignature}
                className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Clear Signature
              </button>
            </div>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
              {error}
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-between gap-4">
            <button
              onClick={() => setStep('review')}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
            >
              Back
            </button>
            <button
              onClick={handleSubmitSignature}
              disabled={!signatureData}
              className="px-6 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              Submit Signature
            </button>
          </div>
        </div>
      </div>
    );
  }

  return null;
}

