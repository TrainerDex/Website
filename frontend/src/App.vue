<template>
    <div id="app">
        <md-app>
            <md-app-toolbar class="md-primary" md-elevation="0">
                <md-button class="md-icon-button" @click="toggleMenu" v-if="!menuVisible">
                    <md-icon>menu</md-icon>
                </md-button>
                <span class="md-title">My Title</span>
            </md-app-toolbar>
            
            <md-app-drawer :md-active.sync="menuVisible" md-persistent="mini" md-swipeable>
                <md-toolbar class="md-transparent" md-elevation="0">
                    <span>Navigation</span>
                    
                    <div class="md-toolbar-section-end">
                        <md-button class="md-icon-button md-dense" @click="toggleMenu">
                            <md-icon>keyboard_arrow_left</md-icon>
                        </md-button>
                    </div>
                </md-toolbar>
                
                <md-list>
                    <md-list-item href="/">
                        <md-icon>home</md-icon>
                        <span class="md-list-item-text">Home</span>
                    </md-list-item>
                    
                    <md-list-item>
                        <md-icon>leaderboard</md-icon>
                        <span class="md-list-item-text">Leaderboard</span>
                    </md-list-item>
                    
                    <md-list-item>
                        <md-icon>account_circle</md-icon>
                        <span class="md-list-item-text">Profile</span>
                    </md-list-item>
                    
                    <md-list-item>
                        <md-icon>people</md-icon>
                        <span class="md-list-item-text">Trainer Codes</span>
                    </md-list-item>
                    
                    <md-list-item>
                        <md-icon>add</md-icon>
                        <span class="md-list-item-text">Submit</span>
                    </md-list-item>
                </md-list>
            </md-app-drawer>
            
            <md-app-content>
                <router-view />
            </md-app-content>
        </md-app>
    </div>
</template>

<script>
export default {
    name: 'PersistentMini',
    data: () => ({
        menuVisible: false
    }),
    methods: {
        toggleMenu () {
            this.menuVisible = !this.menuVisible
        }
    }
}
</script>

<style>
.md-app {
    height: 100vh;
}
</style>
