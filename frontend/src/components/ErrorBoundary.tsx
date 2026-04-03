import { Component, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error) {
    return { error };
  }

  render() {
    if (this.state.error) {
      return (
        <div className="min-h-screen bg-gray-950 flex items-center justify-center p-8">
          <div className="bg-red-900/50 border border-red-700 rounded-lg p-6 max-w-2xl w-full">
            <h2 className="text-xl font-bold text-red-200 mb-2">Something went wrong</h2>
            <pre className="text-sm text-red-300 whitespace-pre-wrap break-words">
              {this.state.error.message}
            </pre>
            <pre className="text-xs text-red-400 mt-2 whitespace-pre-wrap break-words max-h-48 overflow-y-auto">
              {this.state.error.stack}
            </pre>
            <button
              onClick={() => this.setState({ error: null })}
              className="mt-4 px-4 py-2 bg-red-700 text-white rounded hover:bg-red-600"
            >
              Try Again
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
