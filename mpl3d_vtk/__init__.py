"""MATLAB-style 3D graphics powered by VTK."""
from .scene import (Graphic, VtkAxes, alim, axis, caxis, camlight, camproj, clim,
                    close, colorbar, colormap, daspect, drawnow, figure, gca,
                    grid, hidden, hold, light, lightangle, lighting, material,
                    pbaspect, savefig, set, shading, show, subplot, text, title,
                    view, xlabel, ylabel, zlabel)
from .charts import (addpoints, animatedline, bar3, bar3h, bubblechart3, clearpoints,
                     comet3, fplot3, getpoints, histogram2, line, pie3, plot3, scatter3,
                     stem3, streamparticles, swarmchart3)
from .surfaces import (clabel, contour3, cylinder, ellipsoid, fill3, fmesh, fsurf, mesh,
                       meshc, meshz, patch, pcolor, peaks, ribbon, sphere, surf,
                       surf2patch, surfc, surface, surfl, surfnorm, tetramesh,
                       trimesh, trisurf, waterfall)
from .volumes import (contourslice, fimplicit3, flow, isocaps, isocolors, isonormals,
                      isosurface, isosurface_geometry, reducepatch, reducevolume, shrinkfaces, slice,
                      smooth3, subvolume, volumebounds)
from .vectors import (coneplot, curl, divergence, interpstreamspeed, quiver3, stream2, stream3,
                      streamline, streamribbon, streamslice, streamtube)
from .spatial import alphashape, pcshow, pcshowpair, plotTransforms, volshow
from .graphs import graphplot, plot
from .planes import image, imagesc

__version__ = "0.4.0"
