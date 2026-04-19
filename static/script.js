const dropArea = document.getElementById('drop-area');
const fileElem = document.getElementById('fileElem');
const uploadBtn = document.getElementById('uploadBtn');
const loading = document.getElementById('loading');
const uploadSection = document.getElementById('upload-section');
const verifySection = document.getElementById('verify-section');
const successSection = document.getElementById('success-section');
const formFields = document.getElementById('form-fields');
const confidenceScore = document.getElementById('confidence-score');
const providerName = document.getElementById('provider-name');
const verifyForm = document.getElementById('verify-form');
const securityOverlay = document.getElementById('security-overlay');
const loginBtn = document.getElementById('loginBtn');
const accessKeyInput = document.getElementById('accessKey');
const errorMsg = document.getElementById('error-msg');

// --- Security Logic ---
loginBtn.addEventListener('click', handleLogin);
accessKeyInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleLogin();
});

async function handleLogin() {
    const key = accessKeyInput.value;
    if (!key) return;

    try {
        const res = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key })
        });

        if (res.ok) {
            securityOverlay.classList.add('hidden');
            localStorage.setItem('energy_token', key);
        } else {
            errorMsg.classList.remove('hidden');
            accessKeyInput.value = '';
        }
    } catch (err) {
        alert("Security check failed. Try again later.");
    }
}

// Auto-login if token exists
// (Disabled for first run to ensure user sees design)
// if (localStorage.getItem('energy_token')) {
//    securityOverlay.classList.add('hidden');
// }

// --- Upload Logic ---
uploadBtn.addEventListener('click', () => fileElem.click());

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
  dropArea.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults (e) {
  e.preventDefault();
  e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
  dropArea.addEventListener(eventName, () => dropArea.classList.add('dragover'), false)
});

['dragleave', 'drop'].forEach(eventName => {
  dropArea.addEventListener(eventName, () => dropArea.classList.remove('dragover'), false)
});

dropArea.addEventListener('drop', (e) => {
  let dt = e.dataTransfer;
  let files = dt.files;
  handleFiles(files);
});

fileElem.addEventListener('change', function() {
    handleFiles(this.files);
});

async function handleFiles(files) {
    if(!files || files.length === 0) return;
    const file = files[0];
    
    // UI states
    dropArea.classList.add("hidden");
    loading.classList.remove("hidden");
    
    const formData = new FormData();
    formData.append("file", file);
    
    try {
        const response = await fetch("/upload", {
            method: "POST",
            headers: {
                'X-Access-Key': localStorage.getItem('energy_token') || ''
            },
            body: formData
        });
        
        if (!response.ok) throw new Error("Processing failed. Please check your document.");
        
        const data = await response.json();
        renderVerificationForm(data);
        
    } catch(err) {
        alert("Extraction Error: " + err.message);
        dropArea.classList.remove("hidden");
        loading.classList.add("hidden");
    }
}

function renderVerificationForm(data) {
    uploadSection.classList.add("hidden");
    verifySection.classList.remove("hidden");
    
    let conf = data.overall_confidence ? (data.overall_confidence * 100).toFixed(1) : "95";
    confidenceScore.innerText = `${conf}% Confidence`;
    
    if (conf < 70 || data.review_required) {
        confidenceScore.classList.add('warning');
        confidenceScore.innerText += " (Review Required)";
    } else {
        confidenceScore.classList.remove('warning');
    }
    
    providerName.innerText = `Detected Provider: ${data.provider || 'MSEDCL'}`;
    
    formFields.innerHTML = "";
    
    const displayNames = {
        consumer_name: "Consumer Name",
        consumer_number: "Consumer Number",
        bill_month: "Bill Month",
        bill_amount: "Bill Amount (₹)",
        units: "Units Consumed",
        sanctioned_load: "Sanctioned Load",
        fixed_charges: "Fixed Charges (₹)",
        connection_type: "Tariff / Connection"
    };

    const fields = data.fields || data; // Handle different wrapper styles

    for(const key in displayNames) {
        const fieldData = fields[key] || { value: "", confidence: 1 };
        const isLowConf = fieldData.confidence < 0.70;
        
        let html = `
            <div class="form-group">
                <label>${displayNames[key]}</label>
                <input type="text" name="${key}" value="${fieldData.value || ''}" 
                       style="${isLowConf ? 'border-color: var(--error-color)' : ''}">
            </div>
        `;
        formFields.innerHTML += html;
    }
}

verifyForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const finalData = {};
    const formData = new FormData(verifyForm);
    for(let [key, value] of formData.entries()) {
        finalData[key] = { value: value };
    }
    
    try {
        const response = await fetch("/generate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Access-Key": localStorage.getItem('energy_token') || ''
            },
            body: JSON.stringify({fields: finalData})
        });
        
        if (!response.ok) throw new Error("Excel generation failed");
        
        verifySection.classList.add('hidden');
        successSection.classList.remove('hidden');
        
    } catch(err) {
        alert(err.message);
    }
});
