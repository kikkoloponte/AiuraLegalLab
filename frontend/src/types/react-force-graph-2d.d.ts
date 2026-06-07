declare module 'react-force-graph-2d' {
  import { FC, MutableRefObject } from 'react'

  export interface NodeObject {
    id: string
    x?: number
    y?: number
    [key: string]: unknown
  }

  export interface LinkObject {
    source: string | NodeObject
    target: string | NodeObject
    [key: string]: unknown
  }

  export interface ForceGraphMethods {
    zoomToFit(ms?: number, px?: number): void
    centerAt(x?: number, y?: number, ms?: number): void
    zoom(k?: number, ms?: number): void
  }

  export interface ForceGraph2DProps {
    graphData?: { nodes: NodeObject[]; links: LinkObject[] }
    nodeId?: string
    nodeColor?: string | ((node: NodeObject) => string)
    nodeLabel?: string | ((node: NodeObject) => string)
    nodeRelSize?: number
    nodeVal?: number | string | ((node: NodeObject) => number)
    linkSource?: string
    linkTarget?: string
    linkColor?: string | ((link: LinkObject) => string)
    linkLabel?: string | ((link: LinkObject) => string)
    linkWidth?: number | ((link: LinkObject) => number)
    linkDirectionalArrowLength?: number | ((link: LinkObject) => number)
    linkDirectionalArrowRelPos?: number
    onNodeClick?: (node: NodeObject, event: MouseEvent) => void
    onNodeHover?: (node: NodeObject | null, prevNode: NodeObject | null) => void
    onLinkClick?: (link: LinkObject, event: MouseEvent) => void
    onBackgroundClick?: (event: MouseEvent) => void
    width?: number
    height?: number
    backgroundColor?: string
    showNavInfo?: boolean
    ref?: MutableRefObject<ForceGraphMethods | undefined>
  }

  const ForceGraph2D: FC<ForceGraph2DProps>
  export default ForceGraph2D
}
