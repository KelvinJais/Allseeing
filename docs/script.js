async function fetchJobs() {
  try {
    const response = await fetch('https://allseeing-website.s3.us-east-1.amazonaws.com/data_for_website.json', { cache: "no-store" });
    const data = await response.json();

    // Show last updated date
    const lastUpdatedElem = document.getElementById('last-updated');
    lastUpdatedElem.textContent = "Last updated: " + data.date;

    const jobsContainer = document.getElementById('jobs-container');
    jobsContainer.innerHTML = ''; // Clear prior content

    const jobs = data.jobs;

    // For each company
    for (const company of Object.keys(jobs)) {
      const jobList = jobs[company];
      if (!jobList.length) continue; // Skip if no jobs

      // Create section for company
      const section = document.createElement('section');
      section.className = "company";

      // Company name as heading
      const h3 = document.createElement('h3');
      h3.textContent = company.charAt(0).toUpperCase() + company.slice(1);
      section.appendChild(h3);

      // Create list of jobs
      const ul = document.createElement('ul');
      ul.className = "jobs";

      jobList.forEach(job => {
        const li = document.createElement('li');
        // Some have url, some don't
        if (job.url) {
          const a = document.createElement('a');
          a.href = job.url;
          a.target = "_blank";
          a.rel = "noopener noreferrer";
          a.textContent = job.title;
          li.appendChild(a);
        } else {
          li.textContent = job.title;
        }
        ul.appendChild(li);
      });

      section.appendChild(ul);
      jobsContainer.appendChild(section);
    }
  } catch (error) {
    const jobsContainer = document.getElementById('jobs-container');
    jobsContainer.innerHTML = '<p style="text-align:center;color:#cf6679;">Failed to load jobs data. Please try again later.</p>';
    console.error('Error fetching jobs:', error);
  }
}

fetchJobs();


