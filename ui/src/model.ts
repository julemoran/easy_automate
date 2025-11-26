export interface Selector {
  alias: string;
  xpath: string;
  visible: boolean | null; // Tristate
}

export interface Page {
  id?: string; // Optional for new pages
  application_id: string;
  name: string;
  url: string;
  can_be_navigated_to: boolean;
  identifying_selectors: Selector[];
  interactive_selectors: Selector[];
}

export interface Application {
  id?: string;
  name: string;
}

// Browser session state
export interface BrowserSession {
  session_id: string;
  is_open: boolean;
}