import type { Application, Page } from './model';

// Helper to handle JSON responses
const handleResponse = async <T>(response: Response): Promise<T> => {
  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }
  // Handle empty responses (like from DELETE)
  if (response.status === 204) return {} as T;
  return response.json();
};

export const api = {
  // Applications
  getApplications: () => 
    fetch('/api/applications').then(r => handleResponse<Application[]>(r)),
  
  createApplication: (name: string) => 
    fetch('/api/applications', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    }).then(r => handleResponse<Application>(r)),

  updateApplication: (app: Application) => 
    fetch(`/api/applications/${app.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: app.name })
    }).then(r => handleResponse<Application>(r)),

  deleteApplication: (id: string) => 
    fetch(`/api/applications/${id}`, { method: 'DELETE' }),

  // Pages
  getPages: () => 
    fetch('/api/pages').then(r => handleResponse<Page[]>(r)),

  createPage: (page: Page) => 
    fetch('/api/pages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(page)
    }).then(r => handleResponse<Page>(r)),

  updatePage: (page: Page) => 
    fetch(`/api/pages/${page.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(page)
    }).then(r => handleResponse<Page>(r)),

  deletePage: (id: string) => 
    fetch(`/api/pages/${id}`, { method: 'DELETE' }),

  // Browser Session Endpoints
  openSession: (timeout?: number) =>
    fetch('/api/browser/open', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(timeout ? { timeout } : {})
    }).then(r => handleResponse<{ session_id: string }>(r)),

  closeSession: (sessionId: string) =>
    fetch(`/api/browser/${sessionId}/close`, { method: 'POST' }),

  navigateToPage: (sessionId: string, pageId: string) =>
    fetch(`/api/browser/${sessionId}/navigate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ page_id: pageId })
    }).then(r => handleResponse<void>(r)),

  clickElement: (sessionId: string, pageId: string, selectorAlias: string) =>
    fetch(`/api/browser/${sessionId}/click`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ page_id: pageId, selector_alias: selectorAlias })
    }).then(r => handleResponse<void>(r)),

  setElementValue: (sessionId: string, pageId: string, selectorAlias: string, value: string) =>
    fetch(`/api/browser/${sessionId}/set-value`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ page_id: pageId, selector_alias: selectorAlias, value })
    }).then(r => handleResponse<void>(r)),

  getElementValue: (sessionId: string, pageId: string, selectorAlias: string) =>
    fetch(`/api/browser/${sessionId}/get-value`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ page_id: pageId, selector_alias: selectorAlias })
    }).then(r => handleResponse<{ value: string }>(r)),

  waitForPage: (sessionId: string, pageId: string, timeout: number = 10) =>
    fetch(`/api/browser/${sessionId}/wait-for-page`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ page_id: pageId, timeout })
    }).then(r => handleResponse<void>(r)),

  checkSelectors: (sessionId: string) =>
    fetch(`/api/browser/${sessionId}/checkSelectors`).then(r => handleResponse<any>(r)),

  getCurrentPage: (sessionId: string) =>
    fetch(`/api/browser/${sessionId}/get-current-page`).then(r => handleResponse<any>(r)),

  takeScreenshot: (sessionId: string) =>
    fetch(`/api/browser/${sessionId}/screenshot`).then(r => r.blob()),

  getDom: (sessionId: string) =>
    fetch(`/api/browser/${sessionId}/dom`).then(r => r.text()),
};