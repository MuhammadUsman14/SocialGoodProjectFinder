document.addEventListener("DOMContentLoaded", function () {
    const categoryDropdown = document.getElementById("category-dropdown");
    const categoryMenu = document.getElementById("category-menu");
    const clearFiltersButton = document.getElementById("clear-filters");

    // Toggle dropdown menu
    categoryDropdown.addEventListener("click", () => {
        categoryMenu.style.display = categoryMenu.style.display === "block" ? "none" : "block";
    });

    // Clear filters
    clearFiltersButton.addEventListener("click", () => {
        const urlParams = new URLSearchParams(window.location.search);
        urlParams.delete("location");
        urlParams.delete("category");
        urlParams.delete("skills");
        urlParams.set("page", 1);
        window.location.search = urlParams.toString();
    });

    // Pagination
    function changePage(newPage) {
        const urlParams = new URLSearchParams(window.location.search);
        urlParams.set('page', newPage);  // Update the page parameter
        window.location.search = urlParams.toString();  // Redirect with updated query string
    }
    
    

    // Hide dropdown menu when clicking outside
    document.addEventListener("click", (e) => {
        if (!categoryDropdown.contains(e.target) && !categoryMenu.contains(e.target)) {
            categoryMenu.style.display = "none";
        }
    });
});

