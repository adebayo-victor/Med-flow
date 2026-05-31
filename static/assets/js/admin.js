document.addEventListener('DOMContentLoaded', ()=>{
    const sidebarToggleBtn = document.getElementById('sidebar-toggle-btn');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const navLinks = document.querySelectorAll('#sidebar nav a');
    const sections = document.querySelectorAll('main section[id]'); // Get all sections with an ID
    // Function to toggle sidebar visibility and overlay
    const toggleSidebar = () => {
        sidebar.classList.toggle('open');
        sidebarOverlay.classList.toggle('active');
    };

    // Function to set active navigation link
    const setActiveLink = (id) => {
        navLinks.forEach(link => {
            if (link.getAttribute('href') === `#${id}`) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    };

    // Event Listeners for sidebar toggle button and overlay
    if (sidebarToggleBtn) {
        sidebarToggleBtn.addEventListener('click', toggleSidebar);
    }
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', toggleSidebar); // Clicking overlay closes sidebar
    }

    // Add click listeners to navigation links
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent default anchor jump behavior
            const targetId = this.getAttribute('href').substring(1); // Get section ID from href (e.g., "dashboard")
            const targetSection = document.getElementById(targetId);

            if (targetSection) {
                // Scroll to the target section with an offset for the fixed header
                window.scrollTo({
                    top: targetSection.offsetTop - 90, // Adjust offset as needed (e.g., header height + some padding)
                    behavior: 'smooth'
                });

                // Manually set the active class immediately on click
                setActiveLink(targetId);

                // Close sidebar on mobile after clicking a link
                if (window.innerWidth < 768) {
                    toggleSidebar();
                }
            }
        });
    });

    // Scroll event to highlight active nav link as user scrolls
    const onScroll = () => {
        let currentActiveSectionId = '';
        const scrollY = window.scrollY; // Current scroll position

        // Iterate through sections to find which one is currently in view
        // Reverse loop helps in cases where sections might overlap or be very close
        for (let i = sections.length - 1; i >= 0; i--) {
            const section = sections[i];
            // Get the position of the section relative to the viewport
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;

            // If the scroll position is within the section, considering an offset
            // The '90' here is an offset to consider the fixed header height
            if (scrollY >= sectionTop - 90 && scrollY < sectionTop + sectionHeight - 90) {
                currentActiveSectionId = section.getAttribute('id');
                break; // Found the active section, no need to check further
            }
        }
        setActiveLink(currentActiveSectionId); // Set the active link
    };

    // Attach scroll event listener to the window
    window.addEventListener('scroll', onScroll);
    
    // Displaying all services
    let iconName = 'fas fa-plus-circle' // Initial default icon
    const icons = document.querySelectorAll('.icon')
    icons.forEach(icon => {
        icon.addEventListener('click', (event)=>{
            const iconClass = icon.getAttribute('icon_class')
            const selectedIconDisplay = document.querySelector('.selected-icon');
            if (selectedIconDisplay) {
                selectedIconDisplay.innerHTML = ''; // Clear previous icon
                iconName = iconClass;
                selectedIconDisplay.appendChild(icon.cloneNode(true));
            }
        })
    });
    // Set initial active link on page load
    onScroll();

    // Updating the clinics info 
    const clinicName = document.getElementById('clinic_name')
    const clinicAddress = document.getElementById('clinic_address')
    const clinicPhone = document.getElementById('clinic_phone')
    const clinicEmail = document.getElementById('clinic_email')
    const clinicHours = document.getElementById('clinic_hours')
    const saveClinicInfo = document.getElementById('save-clinic-info')
    
    if (saveClinicInfo) {
        saveClinicInfo.addEventListener('click', ()=>{
            const payload = {
                name: clinicName.value,
                email: clinicEmail.value,
                phone_number: clinicPhone.value,
                address: clinicAddress.value,
                hours: clinicHours.value
            };
        
            fetch(" http://127.0.0.1:8000/update_clinic_info", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload),
                credentials: 'include' // Added for CORS
            })
            .then(response => {
                if (!response.ok) { // Check for HTTP errors
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log(data.response)
                // Assuming the backend returns the updated clinic info directly
                clinicName.value = data.clinic_name
                clinicEmail.value = data.email
                clinicPhone.value = data.phone_number
                clinicAddress.value = data.address
                clinicHours.value = data.operating_hours
            }) 
            .catch(error => {
                console.error("Fetch error:", error);
            });
        })
    }

    // Service management using event delegation
    const serviceBody = document.querySelector('.service-body'); // The tbody or container for services

    if (serviceBody) {
        serviceBody.addEventListener('click', (event) => {
            const target = event.target;
            const serviceRow = target.closest('tr.service-info'); // Get the closest service row

            if (!serviceRow) return; // Not a click on a service row or its children

            const serviceId = serviceRow.getAttribute('service-id');

            // Handle Delete Service
            if (target.classList.contains('service-delete')) {
                const payload = { id: serviceId };
                fetch(" http://127.0.0.1:8000/delete_service", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload),
                    credentials: 'include' // Added for CORS
                })
                .then(response => {
                    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                    return response.json();
                })
                .then(data => {
                    console.log(data[0].response);
                    serviceRow.remove(); // Remove the row from the DOM
                })
                .catch(error => {
                    console.error("Fetch error:", error);
                });
            }

            // Handle Edit Service
            if (target.classList.contains('service-edit-btn')) {
                // Populate the edit form with data from the clicked row's data attributes
                document.getElementById('edit_service_id').value = serviceId;
                document.getElementById('edit_service_name').value = target.dataset.name;
                document.getElementById('edit_service_price').value = target.dataset.price;
                document.getElementById('edit_service_description').value = target.dataset.description;
                document.getElementById('edit_service_icon').value = target.dataset.icon; // Correctly get the icon class
            }
        });
    }

    // Service update form submission
    const serviceUpdate = document.querySelector('.update-service');
    if (serviceUpdate) {
        serviceUpdate.addEventListener('click', () => {
            const payload = {
                id: document.getElementById('edit_service_id').value,
                name: document.getElementById('edit_service_name').value,
                price: document.getElementById('edit_service_price').value,
                description: document.getElementById('edit_service_description').value,
                icon_class: document.getElementById('edit_service_icon').value // Include icon class in update
            };
        
            fetch(" http://127.0.0.1:8000/update_service", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
                credentials: 'include' // Added for CORS
            })
            .then(response => {
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                return response.json();
            })
            .then(data => {
                console.log(data);
                // Find and update the specific service row in the DOM
                const updatedServiceId = data[0]['id'];
                const serviceRowToUpdate = document.querySelector(`.service-info[service-id="${updatedServiceId}"]`);
                if (serviceRowToUpdate) {
                    serviceRowToUpdate.querySelector('.service-name').textContent = data[0]['name'];
                    serviceRowToUpdate.querySelector('.service-price').textContent = data[0]['price'];
                    // Update the icon class if it changed
                    const serviceIconElement = serviceRowToUpdate.querySelector('.service-icon');
                    if (serviceIconElement) {
                        // Remove all existing fa- classes and add the new one
                        serviceIconElement.className = 'service-icon text-[#E00000] text-xl mr-3 group-hover:scale-110 transition-transform'; // Reset to base classes
                        serviceIconElement.classList.add(data[0]['fa_icon_class']);
                    }
                    // Update data attributes for the edit button for future edits
                    const editButton = serviceRowToUpdate.querySelector('.service-edit-btn');
                    if (editButton) {
                        editButton.setAttribute('data-name', data[0]['name']);
                        editButton.setAttribute('data-price', data[0]['price']);
                        editButton.setAttribute('data-description', data[0]['description']);
                        editButton.setAttribute('data-icon', data[0]['fa_icon_class']);
                    }
                }
            }) 
            .catch(error => {
                console.error("Fetch error:", error);
            });
        });
    }

    // Adding a service
    const addNewServiceBtn = document.getElementById('add-new-service');
    if (addNewServiceBtn) {
        addNewServiceBtn.addEventListener('click', () => {
            const payload = {
                name: document.querySelector('#new_service_name').value,
                price: document.querySelector('#new_service_price').value,
                description: document.querySelector('#new_service_description').value,
                icon_class: iconName // Use the selected iconName
            };
        
            fetch(" http://127.0.0.1:8000/add_service", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
                credentials: 'include' // Added for CORS
            })
            .then(response => {
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                return response.json();
            })
            .then(data => {
                console.log(data[0].response);
                // Assuming data[data.length - 1] is the newly added service object
                const newServiceData = data[data.length - 1]; 
                
                // Clone the first service info row as a template
                const templateServiceRow = document.querySelectorAll('.service-info')[0];
                if (templateServiceRow) {
                    const clonedService = templateServiceRow.cloneNode(true); // Deep clone

                    clonedService.setAttribute('service-id', newServiceData.id);
                    clonedService.querySelector('.service-name').textContent = newServiceData.name;
                    clonedService.querySelector('.service-price').textContent = newServiceData.price;
                    
                    // Update icon class
                    const serviceIconElement = clonedService.querySelector('.service-icon');
                    if (serviceIconElement) {
                        serviceIconElement.className = payload['icon_class'] + 'text-[#E00000] text-xl mr-3 group-hover:scale-110 transition-transform'; // Reset to base classes
                        //serviceIconElement.classList.add(payload['icon_class']);
                        
                    }

                    // Update data attributes for the edit button on the new row
                    const editButton = clonedService.querySelector('.service-edit-btn');
                    if (editButton) {
                        editButton.setAttribute('data-id', newServiceData.id);
                        editButton.setAttribute('data-name', newServiceData.name);
                        editButton.setAttribute('data-price', newServiceData.price);
                        editButton.setAttribute('data-description', newServiceData.description);
                        editButton.setAttribute('data-icon', newServiceData.icon_class);
                    }
                    
                    // The event listeners for delete/edit are handled by delegation on serviceBody,
                    // so no need to re-add them here for the new element.

                    document.querySelector('.service-body').appendChild(clonedService);
                } else {
                    console.warn("No existing service row found to clone for new service.");
                }
            }) 
            .catch(error => {
                console.error("Fetch error:", error);
            });
        });
    }

    const viewAppointments = document.querySelectorAll('.view-appointment')
    const closeViewAppointment = document.querySelector('#closeBookingConfirmationOverlay')
    //close the appointment
    if (closeViewAppointment) {
        closeViewAppointment.addEventListener('click', (event)=>{
            // Ensure .view-appointment-overlay is the correct element to hide the overlay
            const viewAppointmentOverlay = document.querySelector('.view-appointment-overlay');
            if (viewAppointmentOverlay) {
                viewAppointmentOverlay.classList.remove('visible');
            }
            // Clear the content, using '=' instead of '+='
            document.querySelector('#confirmName').textContent = '';
            document.querySelector('#confirmEmail').textContent = '';
            document.querySelector('#confirmPhone').textContent = '';
            document.querySelector('#confirmSymptoms').textContent = '';
            document.querySelector('#confirmStatus').textContent = '';
            document.querySelector('#confirmBill').textContent = '';
        })
    }
    
    //function to view the appointment
    viewAppointments.forEach(viewAppointment => {
        viewAppointment.addEventListener('click', (event)=>{
            const payload = {
                id:event.target.closest('tr').getAttribute('appointment-id')
            };
        
            fetch(" http://127.0.0.1:8000/fetch_appointments", {
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
                console.log(data)
                // Ensure data[0] exists and has a 'response' property before accessing it
                if (data && data.length > 0) {
                    console.log(data[0].response); // Still logging response, assuming it's always there
                    const viewAppointmentOverlay = document.querySelector('.view-appointment-overlay');
                    if (viewAppointmentOverlay) {
                        viewAppointmentOverlay.classList.add('visible');
                    }
                    // Use '=' to set text content, not '+=' to avoid appending on multiple clicks
                    document.querySelector('#confirmName').textContent = data[0].full_name || '';
                    document.querySelector('#confirmEmail').textContent = data[0].email || '';
                    document.querySelector('#confirmPhone').textContent = data[0].phone || '';
                    document.querySelector('#confirmSymptoms').textContent = data[0].notes || '';
                    document.querySelector('#confirmStatus').textContent = data[0].status || '';
                    document.querySelector('#confirmBill').textContent = data[0].bill || '';
                } else {
                    console.warn("No appointment data received.");
                }
            }) 
            .catch(error => {
                console.error("Fetch error:", error);
            });
        })
    })
    //appointment validation
    const validateAppointments = document.querySelector('#validate-appointments')
    const validateAppointmentCard = document.querySelector('#appointment-validity-form')
    const verify = document.querySelector('.verify')
    const closeValidity = document.querySelector('#close-validity')
    if (validateAppointments) {
        validateAppointments.addEventListener('click', (event)=>{
            validateAppointmentCard.classList.add('visible')
        })
    }
    if (closeValidity) {
        closeValidity.addEventListener('click', (event)=>{
            validateAppointmentCard.classList.remove('visible')
        })
    }
    if (verify) {
        verify.addEventListener('click', (event)=>{
            const payload = {
                code:document.querySelector('#appointment-code').value,
                email:document.querySelector('#appointment-email').value
            };
        
            fetch(" http://127.0.0.1:8000/validate_appointment", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload),
                credentials: 'include' // Added for CORS
            })
            .then(response => {
                if (!response.ok) { // Check for HTTP errors
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('status changed: ', data.response)
                // Further actions after validation (e.g., update UI based on response)
            }) 
            .catch(error => {
                console.error("Fetch error:", error);
            });
        })
    }
    
    //set expiry day by sending to backend
    const expiryDays = document.querySelector('#expiry_days')
    const expiryHours = document.querySelector('#expiry_hours')
    const expiryMinutes = document.querySelector('#expiry_minutes')
    const expirySeconds = document.querySelector('#expiry_seconds')
    const setExpiry = document.querySelector('#set-expiry')
    if (setExpiry) {
        setExpiry.addEventListener('click', (event)=>{
            const payload = {
                days: expiryDays.value,
                hours:expiryHours.value,
                minutes:expiryMinutes.value,
                seconds:expirySeconds.value
            };
        
            fetch(" http://127.0.0.1:8000/set_expiry", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload),
                credentials: 'include' // Added for CORS
            })
            .then(response => {
                if (!response.ok) { // Check for HTTP errors
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log(data)
                // Further actions after setting expiry (e.g., confirmation message)
            }) 
            .catch(error => {
                console.error("Fetch error:", error);
            });
        })
    }
    
    //delete members
    const teamMemberContainer = document.querySelector('.team-member-container'); // Container for team members

    if (teamMemberContainer) {
        teamMemberContainer.addEventListener('click', (event) => {
            const target = event.target;
            // Find the closest ancestor with either 'member-info' class or 'member_id' attribute
            const memberInfoDiv = target.closest('.member-info[member_id]'); 

            if (!memberInfoDiv) return; // Not a click on a member info div or its children

            const memberId = memberInfoDiv.getAttribute('member_id');

            // Handle Delete Member
            if (target.classList.contains('member-delete-btn') || target.id === 'member_delete') { // Check for class or ID
                const payload = { id: memberId };
                fetch(" http://127.0.0.1:8000/delete_member", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                })
                .then(response => {
                    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                    return response.json();
                })
                .then(data => {
                    console.log(data);
                    memberInfoDiv.remove(); // Remove the member div from the DOM
                })
                .catch(error => {
                    console.error("Fetch error:", error);
                });
            }

            // Handle Edit Member (assuming a class 'member-edit-btn' for edit)
            if (target.classList.contains('member-edit-btn') || target.id === 'member_edit') { // Check for class or ID
                // Populate the edit form with data from the clicked member's data attributes
                document.getElementById('edit_member_id').value = memberId; // Assuming an edit form with this ID
                document.getElementById('edit_member_name').value = target.dataset.name || '';
                document.getElementById('edit_member_position').value = target.dataset.position || '';
                document.getElementById('edit_member_specialization').value = target.dataset.specialization || '';
                document.getElementById('edit_member_bio').value = target.dataset.bio || '';
                document.getElementById('edit_member_image').value = target.dataset.image || '';
            }
        });
    }

    const addNewMember = document.querySelector('#add-new-member')    
    if (addNewMember) {
        addNewMember.addEventListener('click', (event)=>{
            const payload = {
                name:document.querySelector('#member_name').value,
                position:document.querySelector('#member_position').value,
                specialization:document.querySelector('#member_specialization').value, // Corrected typo: was 'position' twice
                bio:document.querySelector('#member_bio').value,
                email:document.querySelector('#member_email').value,
                phone:document.querySelector('#member_phone').value,
                image_url:document.querySelector('#member_image').value,
            };
        
            fetch(" http://127.0.0.1:8000/add_member", {
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
                console.log(data);
                // Assuming data[0] is the newly added member object
                const newMemberData = data[0]; 

                // Clone the first member-info element as a template
                const templateMember = document.querySelectorAll('.member-info')[0];
                if (templateMember) {
                    const clonedMember = templateMember.cloneNode(true); // Deep clone

                    clonedMember.setAttribute('member_id', newMemberData.id);
                    clonedMember.querySelector('#member-name').textContent = newMemberData.name;
                    clonedMember.querySelector('#member-img').setAttribute('src', newMemberData.image_url);
                    // Corrected: Combine position and specialization for display
                    clonedMember.querySelector('#member-position').textContent = `${newMemberData.position}\n${newMemberData.specialization}`;
                    clonedMember.querySelector('#member-bio').textContent = newMemberData.bio;
                    
                    // Update data attributes for the edit button on the new member
                    const editButton = clonedMember.querySelector('#member_edit'); // Assuming this ID or a class like .member-edit-btn
                    if (editButton) {
                        editButton.setAttribute('member_id', newMemberData.id);
                        editButton.setAttribute('data-name', newMemberData.name);
                        editButton.setAttribute('data-position', newMemberData.position);
                        editButton.setAttribute('data-specialization', newMemberData.specialization);
                        editButton.setAttribute('data-bio', newMemberData.bio);
                        editButton.setAttribute('data-image', newMemberData.image_url);
                    }
                    // Ensure the delete button also has the correct member_id
                    const deleteButton = clonedMember.querySelector('#member_delete'); // Assuming this ID or a class like .member-delete-btn
                    if (deleteButton) {
                        deleteButton.setAttribute('member_id', newMemberData.id);
                    }

                    // The delete/edit listeners are handled by delegation on teamMemberContainer,
                    // so no need to re-add them here for the new element.
                    document.querySelector('.team-member-container').appendChild(clonedMember);
                } else {
                    console.warn("No existing member-info found to clone for new member.");
                }
            })
            .catch(error => {
                console.error("Fetch error:", error);
            });
        });
    }

    // Search Appointment (This block was misplaced inside addNewMember, moving it out)
    const searchBtn = document.querySelector('#search-button')
    const searchInput = document.querySelector('#appointment-search-input')
    if (searchBtn) {
        searchBtn.addEventListener('click', (event)=>{
            const payload = {
                input: searchInput.value
            };
        
            fetch(" http://127.0.0.1:8000/search_appointment", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload),
                credentials: 'include' // Added for CORS
            })
            .then(response => {
                if (!response.ok) { // Check for HTTP errors
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log(data)
                // Assuming data is an array and we want to display the first result
                if (data && data.length > 0) {
                    const appointmentData = data[0];
                    const clone = document.querySelectorAll('.appointment')[0]; // Assuming this is the display area

                    if (clone) {
                        clone.querySelector('.name').textContent = appointmentData.name || '';
                        clone.querySelector('.date').textContent = appointmentData.date || '';
                        clone.querySelector('.time').textContent = appointmentData.time || '';
                        clone.querySelector('.notes').textContent = appointmentData.notes || '';
                        clone.setAttribute('appointment-id', appointmentData.id);
                    } else {
                        console.warn("Appointment display area not found.");
                    }
                } else {
                    console.log("No appointment found for the given input.");
                    // Optionally clear previous display or show a "not found" message
                    const clone = document.querySelectorAll('.appointment')[0];
                    if (clone) {
                        clone.querySelector('.name').textContent = 'N/A';
                        clone.querySelector('.date').textContent = 'N/A';
                        clone.querySelector('.time').textContent = 'N/A';
                        clone.querySelector('.notes').textContent = 'No appointment found.';
                        clone.removeAttribute('appointment-id');
                    }
                }
            })
            .catch(error => {
                console.error("Fetch error:", error);
            });
        })
    }
    //blog deletion
    const blogsDelete = document.querySelectorAll(".delete_blog")
    blogsDelete.forEach(blogDelete => {
        blogDelete.addEventListener("click", (event)=>{
            payload = {
                id: event.target.getAttribute('blog_id')
            }
            fetch(" http://127.0.0.1:8000/delete_blog", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload),
            })
            .then(response => {
                if (!response.ok) { // Check for HTTP errors
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log(data)
                // Assuming data is an array and we want to display the first result
                if (data[0].response === "successful"){
                    event.target.closest('.blog_container').remove()
                    showToast('Blog removed')
                }
            })
            .catch(error => {
                console.error("Fetch error:", error);
            });
        })
    })
    //here is where the chart magic happens
    //obtaining the data
    fetch(" http://127.0.0.1:8000/appointment_trend", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({})  // 👈 this fixes the empty body issue
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        const xValues = data.x_values;
        const yValues = data.y_values;
    
        const ctx = document.getElementById("appointment_chart").getContext("2d");
    
        new Chart(ctx, {
            type: "line",
            data: {
                labels: xValues,
                datasets: [{
                    label: "Appointments",
                    data: yValues,
                    fill: true, // makes the area below line colored
                    tension: 0.3,
                    borderColor: "rgb(255, 0, 0)", // 🟦 pretty blue
                    backgroundColor: "rgba(0, 123, 255, 0.2)", // transparent blue fill
                    pointBackgroundColor: "rgba(0,123,255,1)"
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    })
    .catch(error => {
        console.error("Fetch error:", error);
    });
    //service popularity
    fetch(" http://127.0.0.1:8000/service_popularity")
    .then(response => {
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return response.json();
    })
    .then(data => {
        console.log(data)
        const xValues = data.x_values;
        const yValues = data.y_values;

        new Chart("service_chart", {
            type: "bar",
            data: {
                labels: xValues,
                datasets: [{
                    label: "Service Popularity",
                    backgroundColor: "rgba(0, 128, 255, 0.7)",
                    borderColor: "rgba(0, 64, 128, 1)",
                    borderWidth: 1,
                    data: yValues
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: ctx => `Count: ${ctx.raw}`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        },
                        grid: {
                            color: "rgba(200, 200, 200, 0.2)"
                        }
                    },
                    x: {
                        grid: {
                            color: "rgba(200, 200, 200, 0.05)"
                        }
                    }
                }
            }
        });
    })
    .catch(error => {
        console.error("Fetch error:", error);
    });
    

});
