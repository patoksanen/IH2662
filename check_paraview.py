from pathlib import Path
from paraview.simple import XMLMultiBlockDataReader, GetActiveViewOrCreate, Show, ColorBy, Render, SaveScreenshot
root = Path(__file__).resolve().parent
reader = XMLMultiBlockDataReader(FileName=[str(root / 'results' / 'mos2d.vtm')])
reader.UpdatePipeline()
assert reader.GetDataInformation().GetNumberOfPoints() > 0
view = GetActiveViewOrCreate('RenderView')
display = Show(reader, view)
ColorBy(display, ('POINTS', 'Potential'))
display.RescaleTransferFunctionToDataRange(True, False)
display.SetScalarBarVisibility(view, True)
view.ResetCamera()
Render()
SaveScreenshot(str(root / 'results' / 'paraview_mos2d.png'), view, ImageResolution=[1200, 800])
print('PASS: ParaView read and rendered the DEVSIM VTM.')
