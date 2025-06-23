"use client"

import { useRef, useEffect } from "react"
import { Canvas, useThree } from "@react-three/fiber"
import { OrbitControls, Grid, Text, Line } from "@react-three/drei"
import * as THREE from "three"

interface ModelCanvasProps {
  modelId: string
  selectedTool: string
  selectedElements: string[]
  onElementsSelect: (elements: string[]) => void
}

// Sample structural model data
const sampleNodes = [
  { id: "1", position: [0, 0, 0], restraints: { dx: true, dy: true, dz: true } },
  { id: "2", position: [5, 0, 0], restraints: {} },
  { id: "3", position: [10, 0, 0], restraints: { dx: true, dy: true, dz: true } },
  { id: "4", position: [0, 3, 0], restraints: {} },
  { id: "5", position: [5, 3, 0], restraints: {} },
  { id: "6", position: [10, 3, 0], restraints: {} },
]

const sampleElements = [
  { id: "1", startNode: "1", endNode: "2", type: "beam" },
  { id: "2", startNode: "2", endNode: "3", type: "beam" },
  { id: "3", startNode: "4", endNode: "5", type: "beam" },
  { id: "4", startNode: "5", endNode: "6", type: "beam" },
  { id: "5", startNode: "1", endNode: "4", type: "column" },
  { id: "6", startNode: "2", endNode: "5", type: "column" },
  { id: "7", startNode: "3", endNode: "6", type: "column" },
]

function Node({ node, isSelected, onClick }: any) {
  const meshRef = useRef<THREE.Mesh>(null)
  const hasRestraints = Object.keys(node.restraints).length > 0

  return (
    <group position={node.position}>
      <mesh
        ref={meshRef}
        onClick={(e) => {
          e.stopPropagation()
          onClick(node.id)
        }}
      >
        <sphereGeometry args={[0.1, 16, 16]} />
        <meshStandardMaterial color={isSelected ? "#3b82f6" : hasRestraints ? "#ef4444" : "#10b981"} />
      </mesh>
      {hasRestraints && (
        <mesh position={[0, -0.2, 0]}>
          <boxGeometry args={[0.3, 0.05, 0.3]} />
          <meshStandardMaterial color="#ef4444" />
        </mesh>
      )}
      <Text position={[0, 0.3, 0]} fontSize={0.15} color="#374151" anchorX="center" anchorY="middle">
        {node.id}
      </Text>
    </group>
  )
}

function Element({ element, nodes, isSelected, onClick }: any) {
  const startNode = nodes.find((n: any) => n.id === element.startNode)
  const endNode = nodes.find((n: any) => n.id === element.endNode)

  if (!startNode || !endNode) return null

  const points = [new THREE.Vector3(...startNode.position), new THREE.Vector3(...endNode.position)]

  const color = isSelected ? "#3b82f6" : element.type === "column" ? "#f59e0b" : "#6b7280"

  return (
    <Line
      points={points}
      color={color}
      lineWidth={isSelected ? 4 : 2}
      onClick={(e) => {
        e.stopPropagation()
        onClick(element.id)
      }}
    />
  )
}

function Scene({ selectedElements, onElementsSelect }: any) {
  const { camera } = useThree()

  useEffect(() => {
    camera.position.set(15, 10, 15)
    camera.lookAt(5, 1.5, 0)
  }, [camera])

  const handleNodeClick = (nodeId: string) => {
    console.log("Node clicked:", nodeId)
  }

  const handleElementClick = (elementId: string) => {
    if (selectedElements.includes(elementId)) {
      onElementsSelect(selectedElements.filter((id: string) => id !== elementId))
    } else {
      onElementsSelect([...selectedElements, elementId])
    }
  }

  return (
    <>
      <ambientLight intensity={0.6} />
      <directionalLight position={[10, 10, 5]} intensity={0.8} />

      <Grid
        args={[20, 20]}
        position={[5, 0, 0]}
        cellSize={1}
        cellThickness={0.5}
        cellColor="#e5e7eb"
        sectionSize={5}
        sectionThickness={1}
        sectionColor="#9ca3af"
      />

      {/* Nodes */}
      {sampleNodes.map((node) => (
        <Node key={node.id} node={node} isSelected={selectedElements.includes(node.id)} onClick={handleNodeClick} />
      ))}

      {/* Elements */}
      {sampleElements.map((element) => (
        <Element
          key={element.id}
          element={element}
          nodes={sampleNodes}
          isSelected={selectedElements.includes(element.id)}
          onClick={handleElementClick}
        />
      ))}

      <OrbitControls enablePan enableZoom enableRotate />
    </>
  )
}

export function ModelCanvas({ modelId, selectedTool, selectedElements, onElementsSelect }: ModelCanvasProps) {
  return (
    <div className="w-full h-full bg-gradient-to-br from-blue-50 to-indigo-100">
      <Canvas camera={{ fov: 60, near: 0.1, far: 1000 }}>
        <Scene selectedElements={selectedElements} onElementsSelect={onElementsSelect} />
      </Canvas>
    </div>
  )
}
