// Routes - Using Angular UI-Router
angular.module("ekpogo").config(routesConfig);

function routesConfig($stateProvider, $urlRouterProvider, $locationProvider) {
    // You can use HTML5 mode if you want (instead of /index.html#!/test, you can use /test)
	$locationProvider.html5Mode(false);
  
  	// Define a symbol to use after the hash for Angular (/index.html#!/test)
	$locationProvider.hashPrefix("!");
  
  	// Define a default route if the URL doesn't match a route
	$urlRouterProvider.otherwise("/");
  
    $stateProvider
		.state("home", {
			url: "/",
			templateUrl: "templates/home.html",
      		controller: "GymController",
      		controllerAs: "vm"
   		 })
}
