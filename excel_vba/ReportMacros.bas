Attribute VB_Name = "ReportMacros"
Option Explicit
' ReportMacros.bas - helper macros for Monthly_MI_Pack.xlsx
' Import via VBE: File > Import File, then save the workbook as .xlsm.
' NOTE: written against the pack's layout (Summary, Treaty_Data, DQ_Log). Not executed in Excel by the author:
' run the UAT cases in docs/UAT_Test_Plan.md (section B) before relying on it.

' 1) Refresh data (if the Treaty_Data sheet is a query/connection), recalculate and stamp the run time.
Public Sub RefreshPack()
    Dim cn As WorkbookConnection
    Application.ScreenUpdating = False
    On Error GoTo Fail
    For Each cn In ThisWorkbook.Connections
        cn.Refresh
    Next cn
    Application.CalculateFull
    ThisWorkbook.Worksheets("Summary").Range("A3").Value = "Last refreshed: " & Format(Now, "dd-mmm-yyyy hh:nn")
    Application.ScreenUpdating = True
    MsgBox "Pack refreshed.", vbInformation
    Exit Sub
Fail:
    Application.ScreenUpdating = True
    MsgBox "Refresh failed: " & Err.Description, vbExclamation
End Sub

' 2) Pre-release check: totals tie, no error cells, data-quality status visible. Run before sending the pack.
Public Function ValidatePack() As Boolean
    Dim ws As Worksheet, c As Range, nErr As Long, msg As String
    Dim lastRow As Long, tdTotal As Double, smTotal As Double, dqFail As Long
    For Each ws In ThisWorkbook.Worksheets
        For Each c In ws.UsedRange.Cells
            If IsError(c.Value) Then nErr = nErr + 1
        Next c
    Next ws
    With ThisWorkbook.Worksheets("Treaty_Data")
        lastRow = .Cells(.Rows.Count, "A").End(xlUp).Row
        tdTotal = Application.WorksheetFunction.Sum(.Range("I2:I" & lastRow)) / 1000000#
    End With
    smTotal = ThisWorkbook.Worksheets("Summary").Range("A7").Value
    dqFail = Application.WorksheetFunction.CountIf(ThisWorkbook.Worksheets("DQ_Log").Range("G:G"), "FAIL")
    If nErr > 0 Then msg = msg & "- " & nErr & " cells contain errors" & vbLf
    If Abs(tdTotal - smTotal) > 0.05 Then msg = msg & "- Summary GWP (" & Format(smTotal, "0.0") & "m) does not tie to Treaty_Data (" & Format(tdTotal, "0.0") & "m)" & vbLf
    If msg = "" Then
        ValidatePack = True
        MsgBox "Pack passed validation." & vbLf & dqFail & " data-quality checks currently FAIL (see DQ_Log).", vbInformation
    Else
        ValidatePack = False
        MsgBox "Do NOT send. Issues found:" & vbLf & msg, vbCritical
    End If
End Function

' 3) Export the Summary sheet to PDF next to the workbook.
Public Sub ExportSummaryPdf()
    If Not ValidatePack() Then Exit Sub
    Dim p As String
    p = ThisWorkbook.Path & Application.PathSeparator & "Summary_" & Format(Date, "yyyymmdd") & ".pdf"
    ThisWorkbook.Worksheets("Summary").ExportAsFixedFormat Type:=xlTypePDF, Filename:=p, Quality:=xlQualityStandard
    MsgBox "Saved " & p, vbInformation
End Sub

' 4) Split Treaty_Data into one workbook per region (for regional distribution).
Public Sub SplitByRegion()
    Dim src As Worksheet, regions As Object, r As Variant, i As Long, lastRow As Long
    Dim wbNew As Workbook, outPath As String
    Set src = ThisWorkbook.Worksheets("Treaty_Data")
    Set regions = CreateObject("Scripting.Dictionary")
    lastRow = src.Cells(src.Rows.Count, "A").End(xlUp).Row
    For i = 2 To lastRow
        regions(CStr(src.Cells(i, "D").Value)) = 1
    Next i
    Application.ScreenUpdating = False
    For Each r In regions.Keys
        If src.AutoFilterMode Then src.AutoFilter.ShowAllData
        src.Range("A1:R" & lastRow).AutoFilter Field:=4, Criteria1:=r
        Set wbNew = Workbooks.Add
        src.AutoFilter.Range.SpecialCells(xlCellTypeVisible).Copy wbNew.Worksheets(1).Range("A1")
        wbNew.Worksheets(1).Name = "Treaty_Data"
        outPath = ThisWorkbook.Path & Application.PathSeparator & "Region_" & Replace(Replace(CStr(r), " ", "_"), "&", "and") & ".xlsx"
        wbNew.SaveAs outPath
        wbNew.Close
    Next r
    If src.AutoFilterMode Then src.AutoFilter.ShowAllData
    Application.ScreenUpdating = True
    MsgBox regions.Count & " regional files created.", vbInformation
End Sub
