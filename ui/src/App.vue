
<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light">
    <div class="container-fluid">
      <a class="navbar-brand" href="#">Easy Automate</a>
      <div class="collapse navbar-collapse">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li class="nav-item">
            <router-link to="/page-editor" class="nav-link">Page Editor</router-link>
          </li>
          <li class="nav-item">
            <router-link to="/events-viewer" class="nav-link">Events Viewer</router-link>
          </li>
        </ul>
      </div>
    </div>
  </nav>
  <router-view />
</template>