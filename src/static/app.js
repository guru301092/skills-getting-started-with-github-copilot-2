document.addEventListener("DOMContentLoaded", () => {
  const activitiesListEl = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageEl = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const res = await fetch("/activities");
      if (!res.ok) throw new Error("Failed to load activities");
      const data = await res.json();
      console.log("Fetched activities:", data);
      renderActivities(data);
      populateActivityOptions(data);
    } catch (err) {
      activitiesListEl.innerHTML = `<p class="error">Unable to load activities.</p>`;
      console.error(err);
    }
  }

  function renderActivities(data) {
    activitiesListEl.innerHTML = "";
    for (const [name, info] of Object.entries(data)) {
      const card = document.createElement("div");
      card.className = "activity-card";

      // title
      const title = document.createElement("h4");
      title.textContent = name;
      card.appendChild(title);

      // description
      const desc = document.createElement("p");
      desc.textContent = info.description || "";
      card.appendChild(desc);

      // schedule and capacity
      const meta = document.createElement("p");
      meta.innerHTML = `<strong>Schedule:</strong> ${info.schedule} <br /><strong>Capacity:</strong> ${info.participants.length}/${info.max_participants}`;
      card.appendChild(meta);

      // participants section
      const participantsWrap = document.createElement("div");
      participantsWrap.className = "participants";

      const participantsTitle = document.createElement("h5");
      participantsTitle.innerHTML = `Participants <span class="participant-count">${info.participants.length}</span>`;
      participantsWrap.appendChild(participantsTitle);

      const ul = document.createElement("ul");
      ul.className = "participant-list";

      if (info.participants && info.participants.length > 0) {
        info.participants.forEach(p => {
          const li = document.createElement("li");
          li.className = "participant-item";

          const span = document.createElement("span");
          span.className = "participant-email";
          span.textContent = p;

          const btn = document.createElement("button");
          btn.className = "remove-participant";
          btn.setAttribute("aria-label", `Remove ${p} from ${name}`);
          btn.dataset.activity = name;
          btn.dataset.email = p;
          btn.innerHTML = "✖";

          li.appendChild(span);
          li.appendChild(btn);
          ul.appendChild(li);
        });
      } else {
        const empty = document.createElement("li");
        empty.textContent = "No participants yet";
        ul.appendChild(empty);
      }

      participantsWrap.appendChild(ul);
      card.appendChild(participantsWrap);

      activitiesListEl.appendChild(card);
    }
  }

  // Event delegation for remove participant buttons
  activitiesListEl.addEventListener("click", async (e) => {
    const btn = e.target.closest(".remove-participant");
    if (!btn) return;
    const activity = btn.dataset.activity;
    const email = btn.dataset.email;
    if (!activity || !email) return;

    try {
      const encodedActivity = encodeURIComponent(activity);
      const res = await fetch(`/activities/${encodedActivity}/participants?email=${encodeURIComponent(email)}`, {
        method: "DELETE"
      });
      const json = await res.json();
      if (!res.ok) {
        showMessage(json.detail || "Failed to remove participant.", "error");
        return;
      }
      showMessage(json.message || "Participant removed.", "success");
      await fetchActivities();
    } catch (err) {
      console.error(err);
      showMessage("Network error while removing participant.", "error");
    }
  });

  function populateActivityOptions(data) {
    // clear existing options except the placeholder
    const placeholder = activitySelect.querySelector("option[value='']");
    activitySelect.innerHTML = "";
    if (placeholder) activitySelect.appendChild(placeholder);

    for (const name of Object.keys(data)) {
      const opt = document.createElement("option");
      opt.value = name;
      opt.textContent = name;
      activitySelect.appendChild(opt);
    }
  }

  function showMessage(text, type = "info") {
    messageEl.className = `message ${type}`;
    messageEl.textContent = text;
    messageEl.classList.remove("hidden");
    setTimeout(() => {
      messageEl.classList.add("hidden");
    }, 4000);
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value.trim();
    const activity = activitySelect.value;
    if (!email || !activity) {
      showMessage("Please enter your email and choose an activity.", "error");
      return;
    }
    try {
      const encodedActivity = encodeURIComponent(activity);
      console.log(`Signing up ${email} for ${activity}`);
      const res = await fetch(`/activities/${encodedActivity}/signup?email=${encodeURIComponent(email)}`, {
        method: "POST"
      });
      const json = await res.json();
      if (!res.ok) {
        showMessage(json.detail || "Signup failed.", "error");
        return;
      }
      showMessage(json.message || "Signed up successfully!", "success");
      // refresh activities to show updated participants
      console.log("Refreshing activities list...");
      await fetchActivities();
      console.log("Activities list refreshed");
      signupForm.reset();
    } catch (err) {
      console.error(err);
      showMessage("Network error during signup.", "error");
    }
  });

  // Initialize app
  fetchActivities();
});
