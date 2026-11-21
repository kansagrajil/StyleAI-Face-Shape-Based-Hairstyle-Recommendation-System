import subprocess

ps = """
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open('d:\\JIL\\Face Shape Based Hairstyle Recommendation System\\StyleAI_Project_Report_Atmiya_University.docx')
    $pages = $doc.ComputeStatistics(2)
    Write-Output "TOTAL_PAGES:$pages"
    foreach ($p in $doc.Paragraphs) {
        $t = $p.Range.Text.Trim()
        if ($t -match "^(CHAPTER|[0-9]+\\.[0-9]+|INDEX|ABSTRACT|LIST OF|REFERENCES|APPENDIX|ACKNOWLEDGEMENT|CERTIFICATE|CANDIDATE)") {
            $page = $p.Range.Information(3)
            $sub = $t
            if ($sub.Length -gt 45) { $sub = $sub.Substring(0, 45) }
            Write-Output "$sub -> Page $page"
        }
    }
    $doc.Close([ref]$false)
} finally {
    $word.Quit()
}
"""

res = subprocess.run(["powershell", "-Command", ps], capture_output=True, text=True)
print("STDOUT:")
print(res.stdout)
