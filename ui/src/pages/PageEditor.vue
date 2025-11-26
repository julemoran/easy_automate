<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { provide } from 'vue';
import type { Application, Page, BrowserSession } from '../model';
import { api } from '../api';

import ApplicationList from '../components/ApplicationList.vue';
import PageList from '../components/PageList.vue';
import PageEditor from '../components/PageEditor.vue';

// State
const applications = ref<Application[]>([]);
const pages = ref<Page[]>([]);
const selectedApp = ref<Application | null>(null);
const selectedPage = ref<Page | null>(null);

// Browser session state
const browserSession = ref<BrowserSession | null>(null);
const sessionLoading = ref(false);
// Provide browserSession for child components
provide('browserSession', browserSession);

// Restore browser session from localStorage if present
const BROWSER_SESSION_KEY = 'browserSession';
const loadBrowserSession = () => {
  const raw = localStorage.getItem(BROWSER_SESSION_KEY);
  if (raw) {
    try {
      const parsed = JSON.parse(raw);
      if (parsed && parsed.session_id) {
        browserSession.value = parsed;
      }
    } catch {}
  }
};

const saveBrowserSession = () => {
  if (browserSession.value && browserSession.value.session_id) {
    localStorage.setItem(BROWSER_SESSION_KEY, JSON.stringify(browserSession.value));
  } else {
    localStorage.removeItem(BROWSER_SESSION_KEY);
  }
};

// Computed
const pagesForSelectedApp = computed(() => {
  if (!selectedApp.value) return [];
  return pages.value.filter(p => p.application_id === selectedApp.value?.id);
});

// Actions
const loadData = async () => {
  const [appsData, pagesData] = await Promise.all([
    api.getApplications(),
    api.getPages()
  ]);
  applications.value = appsData;
  
  // Clean selector visibility data (handle legacy python True/False strings if necessary)
  // Note: Assuming the API strictly follows the new interface, but normalizing just in case
  pages.value = pagesData.map(p => ({
    ...p,
    identifying_selectors: (p.identifying_selectors || []).map(s => ({...s, visible: normalizeVisible(s.visible)})),
    interactive_selectors: (p.interactive_selectors || []).map(s => ({...s, visible: normalizeVisible(s.visible)}))
  }));

  // Re-establish selection if objects were replaced
  if (selectedApp.value) {
    selectedApp.value = applications.value.find(a => a.id === selectedApp.value?.id) || null;
  }
  if (selectedPage.value) {
    selectedPage.value = pages.value.find(p => p.id === selectedPage.value?.id) || null;
  }
};

const normalizeVisible = (val: any): boolean | null => {
  if (val === 'True') return true;
  if (val === 'False') return false;
  if (val === true || val === false) return val;
  return null;
};

// App Handlers
const handleAppSelect = (app: Application) => {
  selectedApp.value = app;
  selectedPage.value = null;
};

const handleAppCreate = async (name: string) => {
  await api.createApplication(name);
  await loadData();
};

const handleAppUpdate = async (app: Application) => {
  await api.updateApplication(app);
  await loadData();
};

const handleAppDelete = async (id: string) => {
  if (!confirm('Are you sure?')) return;
  await api.deleteApplication(id);
  if (selectedApp.value?.id === id) {
    selectedApp.value = null;
    selectedPage.value = null;
  }
  await loadData();
};

// Page Handlers
const handlePageCreate = async (name: string) => {
  if (!selectedApp.value) return;
  const newPage: Page = {
    application_id: selectedApp.value.id!,
    name: name,
    url: '',
    can_be_navigated_to: false,
    identifying_selectors: [],
    interactive_selectors: []
  };
  await api.createPage(newPage);
  await loadData();
};

const handlePageUpdate = async (page: Page) => {
  // Filter out empty selectors before sending
  const cleanSelectors = (arr: any[]) => arr.filter(s => s.alias && s.xpath);
  const payload = {
    ...page,
    identifying_selectors: cleanSelectors(page.identifying_selectors),
    interactive_selectors: cleanSelectors(page.interactive_selectors)
  };
  
  await api.updatePage(payload);
  await loadData();
};

const handlePageDelete = async (id: string) => {
  if (!confirm('Delete page?')) return;
  await api.deletePage(id);
  if (selectedPage.value?.id === id) selectedPage.value = null;
  await loadData();
};

// Browser session handlers
const handleOpenSession = async () => {
  sessionLoading.value = true;
  try {
    const result = await api.openSession();
    browserSession.value = { session_id: result.session_id, is_open: true };
    saveBrowserSession();
  } catch (e) {
    alert('Failed to open browser session');
  } finally {
    sessionLoading.value = false;
  }
};

const handleCloseSession = async () => {
  if (!browserSession.value?.session_id) return;
  sessionLoading.value = true;
  try {
    await api.closeSession(browserSession.value.session_id);
    browserSession.value = null;
    saveBrowserSession();
  } catch (e) {
    alert('Failed to close browser session');
  } finally {
    sessionLoading.value = false;
  }
};

onMounted(() => {
  loadBrowserSession();
  loadData();
});
</script>

<template>
  <div class="container-fluid mt-4">
    <div class="row" style="height: 90vh;">
      <div class="col-md-4" style="overflow-y: auto; max-height: 100%; border-right: 1px solid #dee2e6;">
        <!-- Browser session controls -->
        <div class="mb-3">
          <button 
            class="btn btn-primary me-2"
            :disabled="browserSession && browserSession.is_open || sessionLoading"
            @click="handleOpenSession"
          >
            Open Browser Session
          </button>
          <button 
            class="btn btn-danger"
            :disabled="!browserSession || !browserSession.is_open || sessionLoading"
            @click="handleCloseSession"
          >
            Close Browser Session
          </button>
          <span v-if="browserSession && browserSession.is_open" class="ms-2 text-success">
            Session Active (ID: {{ browserSession.session_id }})
          </span>
        </div>

        <ApplicationList 
          :applications="applications" 
          :selectedAppId="selectedApp?.id"
          @select="handleAppSelect"
          @create="handleAppCreate"
          @delete="handleAppDelete"
          @update="handleAppUpdate"
        />

        <hr />

        <div v-if="selectedApp">
          <PageList 
            :application="selectedApp"
            :pages="pagesForSelectedApp"
            :selectedPageId="selectedPage?.id"
            @update-app="handleAppUpdate"
            @select-page="selectedPage = $event"
            @delete-page="handlePageDelete"
            @create-page="handlePageCreate"
            @update-page="handlePageUpdate"
          />
        </div>
        <div v-else class="text-muted">
          Select an application to see pages.
        </div>
      </div>

      <div class="col-md-8" style="overflow-y: auto; max-height: 100%;">
        <div v-if="selectedPage">
          <PageEditor 
            :page="selectedPage" 
            @save="handlePageUpdate" 
          />
        </div>
        <div v-else class="alert alert-light mt-4">
          Select a page to edit details.
        </div>
      </div>
    </div>
  </div>
</template>
