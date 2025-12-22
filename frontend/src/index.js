import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

// Debug error capture - POST all errors to /api/debug/errors/
const DEBUG_ENDPOINT = process.env.NODE_ENV === 'production'
  ? '/api/debug/errors/'
  : 'http://127.0.0.1:8000/api/debug/errors/';

const postError = (errorData) => {
  fetch(DEBUG_ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ...errorData,
      url: window.location.href,
      userAgent: navigator.userAgent,
    }),
  }).catch(() => {}); // Silently fail if debug endpoint is down
};

// Capture uncaught errors
window.onerror = (message, filename, lineno, colno, error) => {
  postError({
    type: 'window.onerror',
    message: String(message),
    filename,
    lineno,
    colno,
    stack: error?.stack || '',
  });
  return false; // Let default handler run too
};

// Capture unhandled promise rejections
window.onunhandledrejection = (event) => {
  postError({
    type: 'unhandledrejection',
    message: String(event.reason?.message || event.reason),
    stack: event.reason?.stack || '',
  });
};

// Capture React errors via console.error override
const originalConsoleError = console.error;
console.error = (...args) => {
  postError({
    type: 'console.error',
    message: args.map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' '),
  });
  originalConsoleError.apply(console, args);
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
