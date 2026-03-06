const form = document.getElementById("searchForm") as HTMLFormElement;

form?.addEventListener("submit", (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const query = formData.get("query") as string;
  const type = formData.get("type") as string;

  if (!query) {
    alert("Please enter a search term");
    return;
  }

  console.log("Search Value:", query);
  console.log("Search Type:", type);

  // Example: Call API here
  // fetch(`/search?query=${encodeURIComponent(query)}&type=${type}`)
  //   .then(res => res.json())
  //   .then(data => console.log(data));
});
