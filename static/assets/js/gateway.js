document.addEventListener('DOMContentLoaded', () => {
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const mobileMenu = document.querySelector('#mobile-menu');
    
    // Function to show/hide main menu
    mobileMenuBtn.addEventListener('click', (event) => {
        // Toggles the 'hidden' class:
        // - If 'hidden' is present, it removes it.
        // - If 'hidden' is not present, it adds it.
        mobileMenu.classList.toggle('hidden');
    });
    //required data structures and variables
    var totalServiceCost = 0
    const serviceCostList = []
    const serviceNamesList = []
    let serviceNames = ""
    // Get references to elements
    const servicePriceOverlay = document.getElementById('servicePriceOverlay');
    const closeServicePriceOverlayButton = document.getElementById('closeServicePriceOverlay');
    const viewServicePricesButton = document.getElementById('viewServicePrices'); // Button on the main page
    const serviceList = servicePriceOverlay.querySelector('.service-list'); // The UL inside the overlay
    const cartIconsContainer = document.getElementById('cartIconsContainer'); // The new container for icons within the cart
    const preOrder = document.getElementById('pre-order')
    const BookingButton = document.getElementById("book-session")
    // --- Overlay Visibility Controls ---
    // Ensure overlay is hidden initially
    if (servicePriceOverlay) {
        servicePriceOverlay.classList.remove('visible');
    }

    // Open overlay when "View All Service Prices" button is clicked
    if (preOrder) {
        preOrder.addEventListener('click', () => {
            if (servicePriceOverlay) {
                servicePriceOverlay.classList.add('visible');
            }
        });
    }

    // Close overlay when close button is clicked
    if (closeServicePriceOverlayButton) {
        closeServicePriceOverlayButton.addEventListener('click', () => {
            if (servicePriceOverlay) {
                servicePriceOverlay.classList.remove('visible');
            }
        });
    }
    // --- End Overlay Visibility Controls ---

    // --- Service Item Click Logic (inside the overlay) ---
    if (serviceList) {
        // Fix: Convert HTMLCollection to an Array to use forEach
        const services = Array.from(serviceList.getElementsByTagName('li'));

        services.forEach(serviceLi => { // 'serviceLi' now refers to each <li> element
            serviceLi.addEventListener('click', () => {
                console.log("Service list item clicked:", serviceLi);

                // Find the icon within the clicked <li> element
                const serviceIcon = serviceLi.querySelector('.fas');
                const servicePrice = serviceLi.querySelector('.service-price')
                const serviceName = serviceLi.querySelector('.service-name')
                console.log(servicePrice)
                //add the price to the cost list to be added before booking a session and adds service name to it respective list
                serviceNamesList.push('|' + serviceName.textContent + '|')
                serviceCostList.push(parseInt(servicePrice.textContent))
                if (serviceIcon) {
                    // Clone the icon so it stays in the service list and appears in the cart
                    const clonedIcon = serviceIcon.cloneNode(true);

                    // Optional: Add some styling to the cloned icon for the cart display
                    clonedIcon.classList.remove('text-[#E00000]'); // Remove original color
                    clonedIcon.classList.add('text-white', 'text-2xl', 'p-2', 'bg-[#E00000]', 'rounded-full'); // New styling for cart
                    //removes icon from the cart and from the cost list too and removes icon Name
                    clonedIcon.addEventListener('click', (event)=>{
                        const index = serviceCostList.indexOf(servicePrice.textContent)
                        serviceCostList.splice(index, 1)
                        const nameIndex = serviceNamesList.indexOf(serviceName.textContent)
                        serviceNamesList.splice(nameIndex, 1)
                        event.target.remove()
                    })
                    // Append the cloned icon to the dedicated container inside the cart
                    if (cartIconsContainer) {
                        cartIconsContainer.appendChild(clonedIcon);
                        //append the service name
                        console.log("Icon appended to cart:", clonedIcon);
                    } else {
                        console.warn("Cart icons container not found!");
                    }
                } else {
                    console.log("No .fas icon found in this service list item.");
                }
            });
        });
    } else {
        console.warn("Service list UL (.service-list) not found inside the overlay. Check your HTML structure.");
    }
    //display confirmation card to submit to backend
    const bookingConfirmationOverlay = document.getElementById("bookingConfirmationOverlay")
    const closeBookingConfirmationOverlay = document.getElementById("closeBookingConfirmationOverlay")
    const formName = document.getElementById('name')
    const formEmail = document.getElementById('email')
    const formPhone = document.getElementById('phone')
    const formSymptoms = document.getElementById('symptoms')
    //confirmation overlay displays
    const confirmName = document.getElementById('confirmName')
    const confirmEmail = document.getElementById('confirmEmail')
    const confirmPhone = document.getElementById('confirmPhone')
    const confirmBill = document.getElementById('confirmBill')
    const confirmSymptoms = document.getElementById('confirmSymptoms')
    //input to be sent to the backend
    const Name = document.getElementById('hidden-name')
    const Email = document.getElementById('hidden-email')
    const Phone = document.getElementById('hidden-phone')
    const Bill = document.getElementById('hidden-bill')
    const Services = document.getElementById('hidden-services')
    const Symptoms = document.getElementById('hidden-symptoms')
    //service icons
    const confirmedServiceIcons = document.getElementById("confirmedServiceIcons")
    
    BookingButton.addEventListener('click', ()=>{
        if (bookingConfirmationOverlay){
            console.log('service cost list', serviceCostList)
            //summing up the bill from the cost list
            totalServiceCost = serviceCostList.reduce((sum, price) => sum + price, 0); // Here, sum starts at 0
            //summing up the content of the list
            serviceNames = serviceNamesList.reduce((string, word) => string + word, '');
            //adding the icons to the confirmation card
            const confirmedIcons = cartIconsContainer.querySelectorAll('.fas')
            console.log(confirmedIcons )
            if(confirmedIcons.length !== 0){
                confirmedIcons.forEach(confirmedIcon=>{
                    confirmedServiceIcons.appendChild(confirmedIcon)
                })
                document.getElementById('no-services').textContent=''
            }else{
                document.getElementById('no-services').textContent = 'No services selected yet'
            }
            //add text content
            //accumulated required content to be sent to the backend, used to be used to fetch data but not anymore
            const payload = {
                name: confirmName.textContent,
                email: confirmEmail.textContent,
                services: serviceNames,
                phone_number: confirmPhone.textContent,
                symptoms: confirmSymptoms.value,
                bill: confirmBill.textContent
            }
            confirmName.textContent = formName.value
            confirmEmail.textContent = formEmail.value
            confirmPhone.textContent = formPhone.value
            confirmSymptoms.textContent = formSymptoms.value
            confirmBill.textContent = totalServiceCost
            Name.value = confirmName.textContent
            Email.value = confirmEmail.textContent
            Phone.value = confirmPhone.textContent
            Symptoms.value = confirmSymptoms.textContent
            Bill.value = confirmBill.textContent
            Services.value = serviceNames
            bookingConfirmationOverlay.classList.add('visible')
            
        }else{
            console.log('bookingConfirmationOverlay does not exist')
        }
        
    })
    closeBookingConfirmationOverlay.addEventListener('click', ()=>{
        if (bookingConfirmationOverlay){
            bookingConfirmationOverlay.classList.remove('visible')
        }else{
            console.log('bookingConfirmationOverlay does not exist')
        }
    })
    //overlaying the testimonial form
    const testimonialForm = document.querySelector('#addTestimonialOverlay')
    const testimonialButton = document.querySelector('#addTestimonialBtn')
    //function to display the testimonial
    testimonialButton.addEventListener('click', (event)=>{
        testimonialForm.classList.add('visible')
    })
    //function to close the testimonial
    const closeTestimonial = document.querySelector('#closeAddTestimonialOverlay')
    closeTestimonial.addEventListener('click', (event)=>{
        testimonialForm.classList.remove('visible')
    })
    //function to submit testimonial
    const submitTestimonial = document.querySelector('#submit-testimonial')
    submitTestimonial.addEventListener('click', (event)=>{
        const payload = {
            name: document.querySelector('#testimonial_name').value,
            email: document.querySelector('#testimonial_email').value,
            quote: document.querySelector('#testimonial_quote_input').value
        };
    
        fetch("http://127.0.0.1:8000/post_testimonial", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        })
        .then(response => {
            if (!response.ok) { // Check for HTTP errors
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data[0].response === "testimonial added to backend"){
                console.log("Data fetched:", data[0].response);
            }else{
                console.log(data[0].response, 'wahala')
            }
            
        }) 
        .catch(error => {
            console.error("Fetch error:", error);
        })
    })
    //view testimonials
    const viewAllTestimonialsBtn = document.getElementById('viewAllTestimonialsBtn');
    const viewAllTestimonialsOverlay = document.getElementById('viewAllTestimonialsOverlay');
    const closeAllTestimonialsOverlay = document.getElementById('closeAllTestimonialsOverlay');
    const testimonialSummaryGrid = document.getElementById('testimonialSummaryGrid');

    const fullTestimonialDisplay = document.getElementById('fullTestimonialDisplay');
    const closeFullTestimonialBtn = document.getElementById('closeFullTestimonial');
    const fullTestimonialAuthor = document.getElementById('fullTestimonialAuthor');
    const fullTestimonialDescription = document.getElementById('fullTestimonialDescription');
    const fullTestimonialQuote = document.getElementById('fullTestimonialQuote');
    const fullTestimonialAvatar = document.getElementById('fullTestimonialAvatar');

    // Function to show an overlay
    function showOverlay(overlayElement) {
        overlayElement.classList.add('visible');
    }

    // Function to hide an overlay
    function hideOverlay(overlayElement) {
        overlayElement.classList.remove('visible');
    }

    // Event listener for "View All Testimonials" button
    if (viewAllTestimonialsBtn) {
        viewAllTestimonialsBtn.addEventListener('click', () => {
            showOverlay(viewAllTestimonialsOverlay);
            // Ensure the full testimonial display is hidden when opening the summary view
            hideOverlay(fullTestimonialDisplay);
        });
    }

    // Event listener for closing the "All Testimonials" overlay
    if (closeAllTestimonialsOverlay) {
        closeAllTestimonialsOverlay.addEventListener('click', () => {
            hideOverlay(viewAllTestimonialsOverlay);
        });
    }

    // Event listener for clicking on individual testimonial summary boxes
    if (testimonialSummaryGrid) {
        testimonialSummaryGrid.addEventListener('click', (event) => {
            const summaryBox = event.target.closest('.testimonial-summary-box');
            if (summaryBox) {
                // Populate the full testimonial display with data from the clicked box
                fullTestimonialAuthor.textContent = summaryBox.dataset.author;
                fullTestimonialDescription.textContent = summaryBox.dataset.description;
                fullTestimonialQuote.textContent = summaryBox.dataset.quote;
                fullTestimonialAvatar.src = summaryBox.dataset.avatar;

                showOverlay(fullTestimonialDisplay); // Show the full testimonial view
            }
        });
    }

    // Event listener for closing the full testimonial display
    if (closeFullTestimonialBtn) {
        closeFullTestimonialBtn.addEventListener('click', () => {
            hideOverlay(fullTestimonialDisplay);
        });
    }
})
