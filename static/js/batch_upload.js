const $ = id => document.getElementById(id);
$("start").addEventListener("click", async () => {
  const files = [...$("files").files];
  if (!files.length) return alert("Choose images first.");
  $("bar").max = files.length; $("bar").value = 0;
  $("start").disabled = true;
  for (const file of files) {
    const fd = new FormData();
    fd.append("image", file);
    fd.append("field_id", $("field_id").value);
    const row = $("out").insertRow();
    row.insertCell().textContent = file.name;
    try {
      const r = await fetch("/analysis/batch", { method: "POST", body: fd });
      const d = await r.json();
      if (d.ok) {
        row.insertCell().textContent = d.percent;
        row.insertCell().textContent = d.severity;
        row.insertCell().innerHTML = `<a href="/results/${d.id}">View</a>`;
      } else { row.insertCell().colSpan = 3; row.cells[1].textContent = "Error: " + d.error; }
    } catch (e) { row.insertCell().colSpan = 3; row.cells[1].textContent = "Error: " + e; }
    $("bar").value++;
  }
  $("start").disabled = false;
});
